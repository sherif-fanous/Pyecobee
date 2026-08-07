class EcobeeException(Exception):
    pass


class EcobeeApiException(EcobeeException):
    def __init__(
        self, message: str, status_code: int | None, status_message: str | None
    ) -> None:
        super().__init__(message)

        self._status_code = status_code
        self._status_message = status_message

    @property
    def status_code(self) -> int | None:
        return self._status_code

    @property
    def status_message(self) -> str | None:
        return self._status_message


class EcobeeAuthorizationException(EcobeeException):
    def __init__(
        self, message: str, error: str, error_description: str, error_uri: str
    ) -> None:
        super().__init__(message)

        self._error = error
        self._error_description = error_description
        self._error_uri = error_uri

    @property
    def error(self) -> str:
        return self._error

    @property
    def error_description(self) -> str:
        return self._error_description

    @property
    def error_uri(self) -> str:
        return self._error_uri


class EcobeeHttpException(EcobeeException):
    pass


class EcobeeRequestsException(EcobeeException):
    pass


class EcobeeDeserializationException(EcobeeException):
    """Raised when a known ecobee response field cannot be converted."""
