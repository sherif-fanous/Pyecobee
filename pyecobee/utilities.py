import json
import logging

import requests

from pyecobee.deserialization import deserialize
from pyecobee.exceptions import (
    EcobeeApiException,
    EcobeeAuthorizationException,
    EcobeeDeserializationException,
    EcobeeException,
    EcobeeHttpException,
)
from pyecobee.objects.status import Status
from pyecobee.responses import EcobeeErrorResponse
from pyecobee.transport import redact

logger = logging.getLogger(__name__)


class Utilities:
    __slots__ = []

    @classmethod
    def object_to_dictionary(cls, object_):
        """Serialize a Pydantic model using ecobee aliases."""

        return object_.model_dump(by_alias=True, exclude_none=True, mode="json")

    @classmethod
    def process_http_response(cls, response, response_class):
        """Deserialize successful responses and translate API error payloads."""

        try:
            payload = response.json()
        except requests.exceptions.JSONDecodeError:
            # A body that is empty or is not JSON at all, such as a proxy error
            # page.
            payload = None

        if response.status_code == requests.codes.ok:
            if payload is None:
                raise EcobeeDeserializationException(
                    f"ecobee response for URL => {response.request.url}\n"
                    f"HTTP code => {response.status_code}\n"
                    "The response body is empty or is not JSON"
                )

            response_object = deserialize(payload, response_class)
            logger.debug(
                "EcobeeResponse:\n[JSON]\n======\n%s".strip(),
                json.dumps(redact(payload), sort_keys=True, indent=2),
            )
            return response_object

        try:
            if isinstance(payload, dict) and "error" in payload:
                error_response = deserialize(payload, EcobeeErrorResponse)
                raise EcobeeAuthorizationException(
                    f"ecobee authorization error encountered for URL => {response.request.url}\n"
                    f"HTTP error code => {response.status_code}\n"
                    f"Error type => {error_response.error}\n"
                    f"Error description => {error_response.error_description}\n"
                    f"Error URI => {error_response.error_uri}",
                    error_response.error,
                    error_response.error_description,
                    error_response.error_uri,
                )

            if isinstance(payload, dict) and "status" in payload:
                status = deserialize(payload["status"], Status)
                raise EcobeeApiException(
                    f"ecobee API error encountered for URL => {response.request.url}\n"
                    f"HTTP error code => {response.status_code}\n"
                    f"Status code => {status.code}\n"
                    f"Status message => {status.message}",
                    status.code,
                    status.message,
                )
            raise EcobeeHttpException(
                f"HTTP error encountered for URL => {response.request.url}\n"
                f"HTTP error code => {response.status_code}"
            )

        except EcobeeException as ecobee_exception:
            logger.exception(
                "%s raised:\n", type(ecobee_exception).__name__, exc_info=True
            )
            raise
