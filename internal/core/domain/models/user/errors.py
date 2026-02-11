from internal.pkg.errors import ValidationError


class UserFirstNameTooLongError(ValidationError):
    code = "USER_FIRST_NAME_TOO_LONG"

    def __init__(self, max_length: int = 10):
        self.max_length = max_length
        super().__init__(param="last_name", max_length=max_length)

    def get_message(self) -> str:
        return f"user first name must be at most {self.max_length} characters"


class UserLastNameTooLongError(ValidationError):
    code = "USER_LAST_NAME_TOO_LONG"

    def __init__(self, max_length: int = 10):
        self.max_length = max_length
        super().__init__(param="last_name", max_length=max_length)

    def get_message(self) -> str:
        return f"user last name must be at most {self.max_length} characters"
