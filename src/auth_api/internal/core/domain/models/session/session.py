import datetime
import uuid

from auth_api.internal.pkg.domain import BaseAggregate
from auth_api.internal.pkg.errors import ParamEmptyError


class Session(BaseAggregate[uuid.UUID]):
    def __init__(self,
                 oid: uuid.UUID,
                 user_id: uuid.UUID,
                 jti: uuid.UUID,
                 device_fingerprint: str,
                 expire_at: datetime.datetime):
        if not user_id:
            raise ParamEmptyError(param='user_id')
        if not jti:
            raise ParamEmptyError(param='jti')
        if not device_fingerprint:
            raise ParamEmptyError(param='device_fingerprint')
        if not expire_at:
            raise ParamEmptyError(param='expire_at')
        super().__init__(oid)
        self.user_id = user_id
        self.jti = jti
        self.device_fingerprint = device_fingerprint
        self.expire_at = expire_at

