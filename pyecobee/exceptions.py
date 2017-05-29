class EcobeeException(Exception):
    pass


class EcobeeApiException(EcobeeException):
    attribute_type_map = {'status_code': 'six.text_type', 'status_message': 'six.text_type'}

    def __init__(self, message, status_code, status_message):
        super(EcobeeApiException, self).__init__(message)
        self._status_code = status_code
        self._status_message = status_message

    @property
    def status_code(self):
        return self._status_code

    @property
    def status_message(self):
        return self._status_message


class EcobeeAuthorizationException(EcobeeException):
    attribute_type_map = {'error': 'six.text_type', 'error_description': 'six.text_type', 'error_uri': 'six.text_type'}

    def __init__(self, message, error, error_description, error_uri):
        super(EcobeeAuthorizationException, self).__init__(message)
        self._error = error
        self._error_description = error_description
        self._error_uri = error_uri

    @property
    def error(self):
        return self._error

    @property
    def error_description(self):
        return self._error_description

    @property
    def error_uri(self):
        return self._error_uri


class EcobeeHttpException(EcobeeException):
    pass


class EcobeeRequestsException(EcobeeException):
    pass
