from werkzeug.security import generate_password_hash, check_password_hash

from auth_api.internal.ports.output.hash_provider import HashProvider


class WerkzeugHashProvider(HashProvider):
    def hash_data(self, data: str) -> str:
        return generate_password_hash(data)

    def verify_data(self, hashed_data: str, data: str) -> bool:
        return check_password_hash(hashed_data, data)

