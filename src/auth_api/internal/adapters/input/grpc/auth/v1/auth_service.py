from Auth_sprint_2.v1 import auth_pb2
from Auth_sprint_2.v1 import auth_pb2_grpc
from Auth_sprint_2.v1 import errors_pb2
from opentelemetry import trace

from auth_api.internal.pkg.errors import UnauthorizedError
from auth_api.internal.ports.output.logger import Logger
from auth_api.internal.ports.output.token_provider import TokenProvider


class AuthGrpcService(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self, token_provider: TokenProvider, logger: Logger):
        self._token_provider = token_provider
        self._logger = logger.branch(component="grpc_auth_service")

    async def VerifyToken(self, request, context):
        logger = self._logger.branch(rpc_method="VerifyToken")
        logger.clear_context()
        span = trace.get_current_span()
        self._attach_request_context(request, span, logger)

        try:
            token = request.access_token.strip()
            if not token:
                return self._error_response(
                    errors_pb2.TOKEN_INVALID,
                    "access_token is required",
                )

            try:
                token_data = self._token_provider.decode_token(token)
            except UnauthorizedError:
                return self._error_response(
                    errors_pb2.TOKEN_INVALID,
                    "token is invalid",
                )

            if token_data.refresh:
                return self._error_response(
                    errors_pb2.TOKEN_IS_REFRESH,
                    "refresh token is not allowed",
                )

            if await self._token_provider.is_token_blacklisted(token_data.jti):
                return self._error_response(
                    errors_pb2.TOKEN_BLACKLISTED,
                    "token is blacklisted",
                )

            return auth_pb2.VerifyTokenResponse(
                user=auth_pb2.UserIdentity(
                    user_id=str(token_data.user.user_id),
                    roles=list(token_data.user.roles),
                    is_superuser=token_data.user.is_superuser,
                )
            )
        finally:
            logger.clear_context()

    @staticmethod
    def _attach_request_context(request, span, logger: Logger) -> None:
        span_context = span.get_span_context()
        if span_context.is_valid:
            logger.bind_context(trace_id=f"{span_context.trace_id:032x}")

        if not request.HasField("context"):
            return

        request_context = request.context
        if request_context.request_id:
            logger.bind_context(request_id=request_context.request_id)
            if span.is_recording():
                span.set_attribute("request.id", request_context.request_id)

        if request_context.user_agent and span.is_recording():
            span.set_attribute("enduser.user_agent", request_context.user_agent)

        if request_context.ip_address and span.is_recording():
            span.set_attribute("client.address", request_context.ip_address)

    @staticmethod
    def _error_response(code: int,
                        message: str) -> auth_pb2.VerifyTokenResponse:
        return auth_pb2.VerifyTokenResponse(
            error=errors_pb2.Error(
                code=code,
                message=message,
            )
        )
