class EcobeeException(Exception):
    pass


class EcobeeApiException(EcobeeException):
    pass


class EcobeeAuthorizationException(EcobeeException):
    pass


class EcobeeHttpException(EcobeeException):
    pass


class EcobeeRequestsException(EcobeeException):
    pass
