import logging

from pyecobee.responses import EcobeeAuthorizeResponse, EcobeeTokensResponse
from pyecobee.services.context import ClientContext
from pyecobee.utilities import Utilities

logger = logging.getLogger(__name__)


class DomainComponent:
    """Base interface for an Ecobee API domain."""

    __slots__ = ("_context",)

    def __init__(self, context: ClientContext) -> None:
        self._context = context


class AuthorizationService(DomainComponent):
    def authorize(
        self, response_type: str = "ecobeePin", timeout: float = 5
    ) -> EcobeeAuthorizeResponse:
        """
        The authorize method allows a 3rd party application to obtain an
        authorization code and a 4 byte alphabetic string which can be
        displayed to the user. The user then logs into the ecobee Portal
        and registers the application using the PIN provided. Once this
        step is completed, the 3rd party application is able to request
        the access and refresh tokens using the request_tokens method.

        :param response_type: This is always "ecobeePin"
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An AuthorizeResponse object
        :rtype: EcobeeAuthorizeResponse
        :raises EcobeeAuthorizationException: If the request results in
        a standard or extended OAuth error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If response_type is not a string
        :raises ValueError: If response_type is not set to "ecobeePin"
        """
        if not isinstance(response_type, str):
            raise TypeError(f"response_type must be an instance of {str}")
        if response_type != "ecobeePin":
            raise ValueError('response_type must be "ecobeePin"')

        response = self._context.transport.request(
            "get",
            ClientContext.AUTHORIZE_URL,
            params={
                "client_id": self._context.application_key,
                "response_type": response_type,
                "scope": self._context.tokens.scope.value,
            },
            timeout=timeout,
        )
        authorize_response = Utilities.process_http_response(
            response, EcobeeAuthorizeResponse
        )

        self._context.store_tokens(
            self._context.tokens.replace(authorization_token=authorize_response.code)
        )

        return authorize_response

    def request_tokens(
        self, grant_type: str = "ecobeePin", timeout: float = 5
    ) -> EcobeeTokensResponse:
        """
        The request_tokens method is used to request the access and
        refresh tokens once the user has authorized the application
        within the ecobee Web Portal.

        :param grant_type: This is always "ecobeePin"
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A TokensResponse object
        :rtype: EcobeeTokensResponse
        :raises EcobeeAuthorizationException: If the request results in
        a standard or extended OAuth error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If grant_type is not a string
        :raises ValueError: If grant_type is not set to "ecobeePin"
        """
        if not isinstance(grant_type, str):
            raise TypeError(f"grant_type must be an instance of {str}")
        if grant_type != "ecobeePin":
            raise ValueError('grant_type must be "ecobeePin"')

        return self._context.issue_tokens(
            grant_type, self._context.tokens.authorization_token, timeout=timeout
        )

    def refresh_tokens(
        self, grant_type: str = "refresh_token", timeout: float = 5
    ) -> EcobeeTokensResponse:
        """
        All access tokens must be refreshed periodically. Token refresh
        reduces the potential and benefit of token theft. Since all
        tokens expire, stolen tokens may only be used for a limited
        time. The refresh_tokens method immediately expires the
        previously issued access and refresh tokens and issues brand new
        tokens.

        :param grant_type: This is always "refresh_token"
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A TokensResponse object
        :rtype: EcobeeTokensResponse
        :raises EcobeeAuthorizationException: If the request results in
        a standard or extended OAuth error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If grant_type is not a string
        :raises ValueError: If grant_type is not set to "refresh_token"
        """
        if not isinstance(grant_type, str):
            raise TypeError(f"grant_type must be an instance of {str}")
        if grant_type != "refresh_token":
            raise ValueError('grant_type must be "refresh_token"')

        return self._context.issue_tokens(
            grant_type, self._context.tokens.refresh_token, timeout=timeout
        )
