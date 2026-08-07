import json

from pyecobee.models import DemandManagement, DemandResponse, Selection
from pyecobee.responses import (
    EcobeeIssueDemandResponsesResponse,
    EcobeeListDemandResponsesResponse,
    EcobeeStatusResponse,
)
from pyecobee.services.context import ClientContext
from pyecobee.utilities import process_http_response


class DomainComponent:
    """Base interface for an Ecobee API domain."""

    __slots__ = ("_context",)

    def __init__(self, context: ClientContext) -> None:
        self._context = context


class DemandService(DomainComponent):
    def list_demand_responses(
        self, timeout: float = 5
    ) -> EcobeeListDemandResponsesResponse:
        """
        The list_demand_responses method returns a list of all demand
        response event which have been issued and have not yet expired.

        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A ListDemandResponses object
        :rtype: EcobeeListDemandResponsesResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        """
        dictionary = {"operation": "list"}

        response = self._context.request(
            "get",
            ClientContext.DEMAND_RESPONSE_URL,
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return process_http_response(response, EcobeeListDemandResponsesResponse)

    def issue_demand_response(
        self,
        selection: Selection,
        demand_response: DemandResponse,
        timeout: float = 5,
    ) -> EcobeeIssueDemandResponsesResponse:
        """
        The issue_demand_response method creates a demand response
        event. Demand EcobeeResponse events may be issued to a set of
        thermostats in order to adjust their program. Demand
        EcobeeResponse events are either optional or mandatory.
        Mandatory events may not be cancelled by the user and must run
        their course.

        :param selection: The selection criteria for update
        :param demand_response: The demand response object to create
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        or demand_response is not an instance of DemandResponse
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if not isinstance(demand_response, DemandResponse):
            raise TypeError(f"demand_response must be an instance of {DemandResponse}")

        dictionary = {
            "selection": selection.to_api_dict(),
            "operation": "create",
            "demandResponse": demand_response.to_api_dict(),
        }

        response = self._context.request(
            "post",
            ClientContext.DEMAND_RESPONSE_URL,
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return process_http_response(response, EcobeeIssueDemandResponsesResponse)

    def cancel_demand_response(
        self, demand_response_ref: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        """
        The cancel_demand_response method cancels a scheduled demand
        response event. When cancelled, the demand response event will
        be removed from all thermostats in the selection.

        :param demand_response_ref: The system generated ID of the
        demand response to cancel
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If demand_response_ref is not a string
        """
        if not isinstance(demand_response_ref, str):
            raise TypeError(f"demand_response_ref must be an instance of {str}")

        dictionary = {
            "operation": "cancel",
            "demandResponse": {"demandResponseRef": demand_response_ref},
        }

        response = self._context.request(
            "post",
            ClientContext.DEMAND_RESPONSE_URL,
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return process_http_response(response, EcobeeStatusResponse)

    def issue_demand_managements(
        self,
        selection: Selection,
        demand_managements: list[DemandManagement],
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The issue_demand_managements method creates demand management
        objects that permit a Utility to forecast and adjust the
        thermostat runtime dynamically with a 5 minute granularity per
        adjustment. Each DM object defines a single hour of a day with
        its 12 5-minute intervals which specify the temperature
        adjustment . The thermostat will apply this temperature
        adjustment on top of the user's program.

        :param selection: The selection criteria for update
        :param demand_managements: A list of demand management objects
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        demand_managements is not a list, or any member of privileges is
        not an instance of DemandManagement
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if not isinstance(demand_managements, list):
            raise TypeError(f"demand_managements must be an instance of {list}")
        for demand_management in demand_managements:
            if not isinstance(demand_management, DemandManagement):
                raise TypeError(
                    "All members of demand_managements must be a an instance "
                    f"of {DemandManagement}"
                )

        dictionary = {
            "selection": selection.to_api_dict(),
            "dmList": [
                demand_management.to_api_dict()
                for demand_management in demand_managements
            ],
        }

        response = self._context.request(
            "post",
            ClientContext.DEMAND_MANAGEMENT_URL,
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return process_http_response(response, EcobeeStatusResponse)
