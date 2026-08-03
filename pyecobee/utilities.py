import json
import logging

import requests

from pyecobee.deserialization import deserialize
from pyecobee.exceptions import (
    EcobeeApiException,
    EcobeeAuthorizationException,
    EcobeeException,
    EcobeeHttpException,
)
from pyecobee.objects.status import Status
from pyecobee.responses import EcobeeErrorResponse
from pyecobee.transport import HttpTransport, redact

logger = logging.getLogger(__name__)
transport = HttpTransport()


class Utilities:
    __slots__ = []

    @classmethod
    def dictionary_to_object(
        cls,
        data,
        property_type,
        response_properties=None,
        parent_classes=None,
        indent=0,
        is_top_level=False,
    ):
        """Convert the legacy top-level wrapper using safe construction.

        ``response_properties``, ``parent_classes``, and ``indent`` remain accepted
        for backward compatibility with callers of the former implementation.
        """
        if len(data) != 1:
            raise ValueError("Expected a single top-level response object")
        name, payload = next(iter(data.items()))
        try:
            model = property_type[name]
        except KeyError as error:
            raise ValueError(f"No model registered for {name}") from error
        return deserialize(payload, model)

    @classmethod
    def make_http_request(
        cls, requests_http_method, url, headers=None, params=None, json_=None, timeout=5
    ):
        """Send a request through the shared session-backed transport."""
        return transport.request(
            requests_http_method.__name__,
            url,
            headers=headers,
            params=params,
            json_=json_,
            timeout=timeout,
        )

    @classmethod
    def object_to_dictionary(cls, object_, class_):
        dictionary = {object_.__class__.__name__: {}}

        for attribute_name in object_.slots():
            attribute_value = getattr(object_, attribute_name)
            if attribute_value is None:
                continue
            api_name = class_.attribute_name_map[attribute_name[1:]]
            if isinstance(attribute_value, list):
                dictionary[object_.__class__.__name__][api_name] = [
                    cls.object_to_dictionary(entry, type(entry))
                    if hasattr(entry, "__slots__")
                    else entry
                    for entry in attribute_value
                ]
            elif hasattr(attribute_value, "__slots__"):
                dictionary[object_.__class__.__name__][api_name] = (
                    cls.object_to_dictionary(attribute_value, type(attribute_value))
                )
            else:
                dictionary[object_.__class__.__name__][api_name] = attribute_value

        return dictionary[object_.__class__.__name__]

    @classmethod
    def process_http_response(cls, response, response_class):
        if response.status_code == requests.codes.ok:
            response_object = deserialize(response.json(), response_class)
            response_object.pretty_format()
            logger.debug(
                "EcobeeResponse:\n[JSON]\n======\n%s".strip(),
                json.dumps(redact(response.json()), sort_keys=True, indent=2),
            )
            return response_object

        try:
            if "error" in response.json():
                error_response = deserialize(response.json(), EcobeeErrorResponse)
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
            if "status" in response.json():
                status = deserialize(response.json()["status"], Status)
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
