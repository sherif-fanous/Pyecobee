import json
import logging

from pyecobee.enumerations import (
    SelectionType,
)
from pyecobee.objects.group import Group
from pyecobee.objects.selection import Selection
from pyecobee.responses import (
    EcobeeGroupsResponse,
)
from pyecobee.services.context import ClientContext
from pyecobee.utilities import Utilities

logger = logging.getLogger(__name__)


class DomainComponent:
    """Base interface for an Ecobee API domain."""

    __slots__ = ("_context",)

    def __init__(self, context: ClientContext) -> None:
        self._context = context


class GroupsService(DomainComponent):
    def request_groups(
        self, selection: Selection, timeout: float = 5
    ) -> EcobeeGroupsResponse:
        """
        The request_groups method retrieves the Group and grouping data
        for the Thermostats registered to the particular User. The User
        here refers to the calling application's user authorization.

        :param selection: The selection criteria for the request. Must
        have selection_type = 'registered'.
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A GroupResponse object
        :rtype: EcobeeGroupsResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        :raises ValueError: If selection.selection_type is not
        "registered"
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if selection.selection_type != SelectionType.REGISTERED:
            raise ValueError(
                f"selection.selection_type must be set to {SelectionType.REGISTERED.value}"
            )

        dictionary = {"selection": Utilities.object_to_dictionary(selection)}

        response = self._context.request(
            "get",
            ClientContext.GROUP_URL,
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeGroupsResponse)

    def update_groups(
        self, selection: Selection, groups: list[Group], timeout: float = 5
    ) -> EcobeeGroupsResponse:
        """
        The update_groups method permits the modification of any
        writable Group object properties.

        :param selection: The selection criteria for the request
        :param groups: The list of Groups to update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A GroupResponse object
        :rtype: EcobeeGroupsResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        groups is not a list, or any member of groups is not an instance
        of Group
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if not isinstance(groups, list):
            raise TypeError(f"groups must be an instance of {list}")
        for group in groups:
            if not isinstance(group, Group):
                raise TypeError(
                    f"All members of groups must be a an instance of {Group}"
                )

        dictionary = {
            "selection": Utilities.object_to_dictionary(selection),
            "groups": [Utilities.object_to_dictionary(group) for group in groups],
        }

        response = self._context.request(
            "post",
            ClientContext.GROUP_URL,
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeGroupsResponse)
