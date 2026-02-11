from internal.pkg.errors import ValidationError


class RoleNameTooShortError(ValidationError):
    code = "ROLE_NAME_TOO_SHORT"

    def __init__(self, min_length: int = 3):
        self.min_length = min_length
        super().__init__(param="name", min_length=min_length)

    def get_message(self) -> str:
        return f"role name must be at least {self.min_length} characters"


class RoleNameTooLongError(ValidationError):
    code = "ROLE_NAME_TOO_LONG"

    def __init__(self, max_length: int = 10):
        self.max_length = max_length
        super().__init__(param="name", max_length=max_length)

    def get_message(self) -> str:
        return f"role name must be at most {self.max_length} characters"
