import typing


class HashProvider(typing.Protocol):
    def hash_data(self, data: str) -> str:
        ...

    def verify_data(self, hashed_data: str, data: str) -> bool:
        ...
