import json
import numbers
from datetime import datetime as DateTime
from typing import Any

from pyecobee.enumerations import (
    AckType,
    FanMode,
    HoldType,
    PlugState,
    SelectionType,
)
from pyecobee.objects.function import Function
from pyecobee.objects.selection import Selection
from pyecobee.objects.thermostat import Thermostat
from pyecobee.responses import (
    EcobeeStatusResponse,
    EcobeeThermostatResponse,
    EcobeeThermostatsSummaryResponse,
)
from pyecobee.services.context import ClientContext
from pyecobee.utilities import Utilities


class DomainComponent:
    """Base interface for an Ecobee API domain."""

    __slots__ = ("_context",)

    def __init__(self, context: ClientContext) -> None:
        self._context = context


class ThermostatsService(DomainComponent):
    def request_thermostats_summary(
        self, selection: Selection, timeout: float = 5
    ) -> EcobeeThermostatsSummaryResponse:
        """
        The request_thermostats_summary method retrieves a list of
        thermostat configuration and state revisions. This is a light-
        weight polling method which will only return the revision
        numbers for the significant portions of the thermostat data. It
        is the responsibility of the caller to store these revisions for
        future determination of whether changes occurred at the next
        poll interval.

        The intent is to permit the caller to determine whether a
        thermostat has changed since the last poll. Retrieval of a whole
        thermostat including runtime data is expensive and impractical
        for large amounts of thermostats such as a management set
        hierarchy, especially if nothing has changed. By storing the
        retrieved revisions, the caller may determine whether to get a
        thermostat and which sections of the thermostat should be
        retrieved.

        :param selection: The selection criteria for the request
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A ThermostatSummaryResponse object
        :rtype: EcobeeThermostatsSummaryResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        dictionary = {"selection": Utilities.object_to_dictionary(selection)}

        response = self._context.request(
            "get",
            ClientContext.THERMOSTAT_SUMMARY_URL,
            params={"json": json.dumps(dictionary, sort_keys=True, indent=2)},
            timeout=timeout,
        )

        return Utilities.process_http_response(
            response, EcobeeThermostatsSummaryResponse
        )

    def request_thermostats(
        self, selection: Selection, timeout: float = 5
    ) -> EcobeeThermostatResponse:
        """
        The request_thermostats method retrieves a selection of
        thermostat data for one or more thermostats. The type of data
        retrieved is determined by the selection argument. The include*
        attributes of the selection argument retrieve specific portions
        of the thermostat. When retrieving thermostats, request only the
        parts of the thermostat you require as the whole thermostat with
        everything can be quite large and generally unnecessary.

        :param selection: The selection criteria for the request
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A ThermostatResponse object
        :rtype: EcobeeThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        dictionary = {"selection": Utilities.object_to_dictionary(selection)}

        response = self._context.request(
            "get",
            ClientContext.THERMOSTAT_URL,
            params={"json": json.dumps(dictionary, sort_keys=True, indent=2)},
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeThermostatResponse)

    def update_thermostats(
        self,
        selection: Selection,
        thermostat: Thermostat | None = None,
        functions: list[Function] | None = None,
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The update_thermostats method permits the modification of any
        writable Thermostat or sub-object property. Thermostats may be
        updated by their writeable properties directly or through the
        Thermostat Functions.

        By including the Thermostat object in the request, any writable
        property may be directly updated in the thermostat. Some
        thermostat child objects are read-only due to either complexity
        in their configuration for which the thermostat functions have
        been created to support, or the object is not modifiable outside
        the physical thermostat (i.e. devices, wifi, etc.)

        Thermostats may also be updated using Thermostat Functions.
        Thermostat Functions provide a way to make more complex updates
        to a thermostat than just setting one or more properties. The
        functions emulate much of the same functionality found on the
        thermostat itself, such as setting a hold, for example. An
        update request may contain any number of functions in the
        request. Each function will be applied in the order they are
        listed in the request.

        :param selection: The selection criteria for the update
        :param thermostat: The thermostat object with properties to
        update
        :param functions: The list of functions to perform on all
        selected thermostats
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        thermostat is not an instance of Thermostat, functions is not a
        list, or any member of functions is not an instance of Function
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if thermostat is not None and not isinstance(thermostat, Thermostat):
            raise TypeError(f"thermostat must be an instance of {Thermostat}")
        if functions is not None and not isinstance(functions, list):
            raise TypeError(f"functions must be an instance of {list}")
        if functions is not None:
            for function_ in functions:
                if not isinstance(function_, Function):
                    raise TypeError(
                        f"All members of functions must be a an instance of {Function}"
                    )

        dictionary = {"selection": Utilities.object_to_dictionary(selection)}

        if thermostat is not None:
            dictionary["thermostat"] = Utilities.object_to_dictionary(thermostat)
        if functions is not None:
            dictionary["functions"] = [
                Utilities.object_to_dictionary(function_) for function_ in functions
            ]

        response = self._context.request(
            "post",
            ClientContext.THERMOSTAT_URL,
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def acknowledge(
        self,
        thermostat_identifier: str,
        ack_ref: str,
        ack_type: AckType,
        remind_me_later: bool = False,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The acknowledge method allows an alert to be acknowledged.

        :param thermostat_identifier: The thermostat identifier to
        acknowledge the alert for
        :param ack_ref: The acknowledge ref of alert
        :param ack_type: The type of acknowledgement. Valid values:
        accept, decline, defer, unacknowledged
        :param remind_me_later: Whether to remind at a later date, if
        this is a defer acknowledgement
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If thermostat_identifier is not a string,
        ack_ref is not a string, ack_type is not a member of AckType,
        remind_me_later is not a boolean, or selection is not an
        instance of Selection
        """
        if not isinstance(thermostat_identifier, str):
            raise TypeError(f"thermostat_identifier must be an instance of {str}")
        if not isinstance(ack_ref, str):
            raise TypeError(f"ack_ref must be an instance of {str}")
        if not isinstance(ack_type, AckType):
            raise TypeError(f"ack_type must be an instance of {AckType}")
        if not isinstance(remind_me_later, bool):
            raise TypeError(f"remind_me_later must be an instance of {bool}")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[
                Function(
                    type="acknowledge",
                    params={
                        "thermostatIdentifier": thermostat_identifier,
                        "ackRef": ack_ref,
                        "ackType": ack_type.value,
                        "remindMeLater": remind_me_later,
                    },
                )
            ],
            timeout=timeout,
        )

    def control_plug(
        self,
        plug_name: str,
        plug_state: PlugState,
        start_date_time: DateTime | None = None,
        end_date_time: DateTime | None = None,
        hold_type: HoldType = HoldType.INDEFINITE,
        hold_hours: int | None = None,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The control_plug method controls the on/off state of a plug by
        setting a hold on the plug, creating a hold for the on or off
        state of the plug for the specified duration.

        Note that an event is created regardless of whether the program
        is in the same state as the requested state.

        :param plug_name: The name of the plug. Ensure each plug has a
        unique name
        :param plug_state: The state to put the plug into. Valid values:
        PlugState.ON, PlugState.OFF, PlugState.RESUME
        :param start_date_time: The start date and time in thermostat
        time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time.
        Must be a timezone aware datetime
        :param hold_type: The hold duration type. Valid values:
        HoldType.DATE_TIME, HoldType.NEXT_TRANSITION,
        HoldType.INDEFINITE, and HoldType.HOLD_HOURS
        :param hold_hours: The number of hours to hold for, used and
        required if holdType='holdHours'
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If plug_name is not a string, plug_state is
        not a member of PlugState, start_date_time is not a datetime,
        end_date_time is not a datetime, hold_type is not a member of
        HoldType, hold_hours is not an integer, or selection is not an
        instance of Selection
        :raises ValueError: If start/end date_times are earlier than
        2008-01-02 00:00:00 +0000, start/end date_times are later than
        2035-01-01 00:00:00 +0000, start_date_time is later than
        end_date_time, end_date_time is None while hold_type is
        HoldType.DATE_TIME, or hold_hours is None while hold_type is
        HoldType.HOLD_HOURS
        """
        if not isinstance(plug_name, str):
            raise TypeError(f"plug_name must be an instance of {str}")
        if not isinstance(plug_state, PlugState):
            raise TypeError(f"plug_state must be an instance of {PlugState}")
        if start_date_time is not None:
            if not isinstance(start_date_time, DateTime):
                raise TypeError(f"start_date_time must be an instance of {DateTime}")
            if start_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "start_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if start_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "start_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if end_date_time is not None:
            if not isinstance(end_date_time, DateTime):
                raise TypeError(f"end_date_time must be an instance of {DateTime}")
            if end_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "end_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if end_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "end_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if (
            start_date_time is not None
            and end_date_time is not None
            and start_date_time >= end_date_time
        ):
            raise ValueError("end_date_time must be later than start_date_time")
        if not isinstance(hold_type, HoldType):
            raise TypeError(f"hold_type must be an instance of {HoldType}")
        if hold_type == HoldType.DATE_TIME and end_date_time is None:
            raise ValueError(
                f"hold_type is {HoldType.DATE_TIME.value}. end_date_time must not be None"
            )
        if hold_hours is not None and not isinstance(hold_hours, int):
            raise TypeError(f"hold_hours must be an instance of {int}")
        if hold_type == HoldType.HOLD_HOURS and hold_hours is None:
            raise ValueError(
                f"hold_type is {HoldType.HOLD_HOURS.value}. hold_hours must not be None"
            )
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        control_plug_parameters: dict[str, Any] = {
            "plugName": plug_name,
            "plugState": plug_state.value,
            "holdType": hold_type.value,
        }

        if start_date_time is not None:
            control_plug_parameters["startDate"] = (
                f"{start_date_time.year}-{start_date_time.month:02}-{start_date_time.day:02}"
            )
            control_plug_parameters["startTime"] = (
                f"{start_date_time.hour:02}:{start_date_time.minute:02}:{start_date_time.second:02}"
            )

        if end_date_time is not None:
            control_plug_parameters["endDate"] = (
                f"{end_date_time.year}-{end_date_time.month:02}-{end_date_time.day:02}"
            )
            control_plug_parameters["endTime"] = (
                f"{end_date_time.hour:02}:{end_date_time.minute:02}:{end_date_time.second:02}"
            )
        if hold_hours is not None:
            control_plug_parameters["holdHours"] = hold_hours

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[Function(type="controlPlug", params=control_plug_parameters)],
            timeout=timeout,
        )

    def create_vacation(
        self,
        name: str,
        cool_hold_temp: float,
        heat_hold_temp: float,
        start_date_time: DateTime | None = None,
        end_date_time: DateTime | None = None,
        fan_mode: FanMode = FanMode.AUTO,
        fan_min_on_time: int = 0,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The create_vacation method creates a vacation event on the
        thermostat. If the start/end date_times are not provided for the
        vacation event, the vacation event will begin immediately and
        last 14 days.

        If both the cool_hold_temp and heat_hold_temp arguments provided
        to this method have the same value, and the Thermostat is in
        auto mode, then the two values will be adjusted during
        processing to be separated by the value stored in
        Thermostat.Settings.heatCoolMinDelta.

        :param name: The vacation event name. It must be unique
        :param cool_hold_temp: The temperature in Fahrenheit to set the
        cool vacation hold at
        :param heat_hold_temp: The temperature in Fahrenheit to set the
        heat vacation hold at
        :param start_date_time: The start date and time in thermostat
        time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time.
        Must be a timezone aware datetime
        :param fan_mode: The fan mode during the vacation. Values: auto,
        on. Default: auto
        :param fan_min_on_time: The minimum number of minutes to run the
        fan each hour. Range: 0-60. Default: 0
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If name is not a string, cool_hold_temp is
        not a real number, heat_hold_temp is not a real number,
        start_date_time is not a datetime, end_date_time is not a
        datetime, fan_mode is not a member of FanMode, fan_min_on_time
        is not an integer, or selection is not an instance of Selection
        :raises ValueError: If cool_hold_temp is lower than -10F,
        cool_hold_temp is higher than 120F, heat_hold_temp is lower than
        45F, heat_hold_temp is higher than 120F, start/end date_times
        are earlier than 2008-01-02 00:00:00 +0000, start/end date_times
        are later than 2035-01-01 00:00:00 +0000, start_date_time is
        later than end_date_time, or fan_min_on_time is less than 0 or
        greater than 60
        """
        if not isinstance(name, str):
            raise TypeError(f"name must be an instance of {str}")
        if not isinstance(cool_hold_temp, numbers.Real):
            raise TypeError(f"cool_hold_temp must be an instance of {numbers.Real}")
        if not (
            ClientContext.MINIMUM_COOLING_TEMPERATURE
            <= float(cool_hold_temp)
            <= ClientContext.MAXIMUM_COOLING_TEMPERATURE
        ):
            raise ValueError(
                f"cool_hold_temp must be between {ClientContext.MINIMUM_COOLING_TEMPERATURE}F and {ClientContext.MAXIMUM_COOLING_TEMPERATURE}F"
            )
        if not isinstance(heat_hold_temp, numbers.Real):
            raise TypeError(f"heat_hold_temp must be an instance of {numbers.Real}")
        if not (
            ClientContext.MINIMUM_HEATING_TEMPERATURE
            <= float(heat_hold_temp)
            <= ClientContext.MAXIMUM_HEATING_TEMPERATURE
        ):
            raise ValueError(
                f"heat_hold_temp must be between {ClientContext.MINIMUM_HEATING_TEMPERATURE}F and {ClientContext.MAXIMUM_HEATING_TEMPERATURE}F"
            )
        if start_date_time is not None:
            if not isinstance(start_date_time, DateTime):
                raise TypeError(f"start_date_time must be an instance of {DateTime}")
            if start_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "start_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if start_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "start_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if end_date_time is not None:
            if not isinstance(end_date_time, DateTime):
                raise TypeError(f"end_date_time must be an instance of {DateTime}")
            if end_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "end_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if end_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "end_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if (
            start_date_time is not None
            and end_date_time is not None
            and start_date_time >= end_date_time
        ):
            raise ValueError("end_date_time must be later than start_date_time")
        if not isinstance(fan_mode, FanMode):
            raise TypeError(f"fan_mode must be an instance of {FanMode}")
        if not isinstance(fan_min_on_time, int):
            raise TypeError(f"fan_min_on_time must be an instance of {int}")
        if fan_min_on_time not in range(61):
            raise ValueError("fan_min_on_time must be between 0 and 60")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        create_vacation_parameters = {
            "name": name,
            "coolHoldTemp": int(float(cool_hold_temp) * 10),
            "heatHoldTemp": int(float(heat_hold_temp) * 10),
            "fan": fan_mode.value,
            "fanMinOnTime": str(fan_min_on_time),
        }

        if start_date_time is not None:
            create_vacation_parameters["startDate"] = (
                f"{start_date_time.year}-{start_date_time.month:02}-{start_date_time.day:02}"
            )
            create_vacation_parameters["startTime"] = (
                f"{start_date_time.hour:02}:{start_date_time.minute:02}:{start_date_time.second:02}"
            )

        if end_date_time is not None:
            create_vacation_parameters["endDate"] = (
                f"{end_date_time.year}-{end_date_time.month:02}-{end_date_time.day:02}"
            )
            create_vacation_parameters["endTime"] = (
                f"{end_date_time.hour:02}:{end_date_time.minute:02}:{end_date_time.second:02}"
            )

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[
                Function(type="createVacation", params=create_vacation_parameters)
            ],
            timeout=timeout,
        )

    def delete_vacation(
        self,
        name: str,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The delete_vacation method deletes a vacation event from a
        thermostat. This is the only way to cancel a vacation event.
        This method is able to remove vacation events not yet started
        and scheduled in the future.

        :param name: The vacation event name to delete
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If name is not a string, or selection is not
        an instance of Selection
        """
        if not isinstance(name, str):
            raise TypeError(f"name must be an instance of {str}")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[Function(type="deleteVacation", params={"name": name})],
            timeout=timeout,
        )

    def reset_preferences(
        self,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The reset_preferences method sets all of the user configurable
        settings back to the factory default values. This method call
        will not only reset the top level thermostat settings such as
        hvacMode, lastServiceDate and vent, but also all of the user
        configurable fields of the Thermostat.Settings and
        Thermostat.Program objects.

        Note that this does not reset all values. For example, the
        installer settings and wifi details remain untouched.

        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[Function(type="resetPreferences")],
            timeout=timeout,
        )

    def resume_program(
        self,
        resume_all: bool = False,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The resume_program method removes the currently running event
        providing the event is not a mandatory demand response event. If
        the resume_all argument is set to False, the top active event is
        removed from the stack and the thermostat resumes its program or
        enters the next event in the stack if one exists. If the
        resume_all argument is set to True, the method resumes all
        events and returns the thermostat to its program.

        :param resume_all: Should the thermostat be resumed to the next
        event (False) or to it's program (True)
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If resume_all is not a boolean, or selection
        is not an instance of Selection
        """
        if not isinstance(resume_all, bool):
            raise TypeError(f"resume_all must be an instance of {bool}")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[
                Function(type="resumeProgram", params={"resumeAll": resume_all})
            ],
            timeout=timeout,
        )

    def send_message(
        self,
        text: str,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The send_message method allows an alert message to be sent to
        the thermostat. The message properties are same as those of the
        Alert Object.

        :param text: The message text to send. Text will be truncated to
        500 characters if longer
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If text is not a string, or selection is not
        an instance of Selection
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be an instance of {str}")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[Function(type="sendMessage", params={"text": text})],
            timeout=timeout,
        )

    def set_hold(
        self,
        cool_hold_temp: float | None = None,
        heat_hold_temp: float | None = None,
        fan_mode: FanMode | None = None,
        hold_climate_ref: str | None = None,
        start_date_time: DateTime | None = None,
        end_date_time: DateTime | None = None,
        hold_type: HoldType = HoldType.INDEFINITE,
        hold_hours: int | None = None,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The set_hold method sets the thermostat into a hold with the
        specified temperature creating a hold for the specified
        duration. Note that an event is created regardless of whether
        the program is in the same state as the requested state.

        There is also support for creating a hold by passing a
        hold_climate_ref argument to this method. When an existing and
        valid Climate.climate_ref value is passed to this method, the
        cool_hold_temp, heat_hold_temp and fan mode from that Climate
        are used in the creation of the hold event. The values from that
        Climate will take precedence over any cool_hold_temp,
        heat_hold_temp and fan mode parameters passed into this method
        separately.

        :param cool_hold_temp: The temperature in Fahrenheit to set the
        cool vacation hold at
        :param heat_hold_temp: The temperature in Fahrenheit to set the
        heat vacation hold at
        :param fan_mode: The fan mode during the hold. Valid values:
        FanMode.AUTO and FanMode.ON
        :param hold_climate_ref: The Climate to use as reference for
        setting the cool_hold_temp, heat_hold_temp and fan settings for
        this hold. If this value is passed the cool_hold_temp and
        heat_hold_temp are not required
        :param start_date_time: The start date and time in thermostat
        time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time.
        Must be a timezone aware datetime
        :param hold_type: The hold duration type. Valid values:
        HoldType.DATE_TIME, HoldType.NEXT_TRANSITION,
        HoldType.INDEFINITE, and HoldType.HOLD_HOURS
        :param hold_hours: The number of hours to hold for, used and
        required if holdType='holdHours'
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If cool_hold_temp is not a real,
        heat_hold_temp is not a real, fan_mode is not a member of
        FanMode, hold_climate_ref is not a string, start_date_time is
        not a datetime, end_date_time is not a datetime, hold_type is
        not a member of HoldType, hold_hours is not an integer, or
        selection is not an instance of Selection
        :raises ValueError: If cool_hold_temp is lower than -10F,
        cool_hold_temp is higher than 120F, heat_hold_temp is lower than
        45F, heat_hold_temp is higher than 120F, cool_hold_temp,
        heat_hold_temp, and hold_climate_ref are None, hold_climate_ref
        is None and either cool_hold_temp or heat_hold_temp are None,
        start/end date_times are earlier than 2008-01-02 00:00:00 +0000,
        start/end date_times are later than 2035-01-01 00:00:00 +0000,
        start_date_time is later than end_date_time, end_date_time is
        None while hold_type is HoldType.DATE_TIME, or hold_hours is
        None while hold_type is HoldType.HOLD_HOURS
        """
        if cool_hold_temp is not None:
            if not isinstance(cool_hold_temp, numbers.Real):
                raise TypeError(f"cool_hold_temp must be an instance of {numbers.Real}")
            if not (
                ClientContext.MINIMUM_COOLING_TEMPERATURE
                <= float(cool_hold_temp)
                <= ClientContext.MAXIMUM_COOLING_TEMPERATURE
            ):
                raise ValueError(
                    f"cool_hold_temp must be between {ClientContext.MINIMUM_COOLING_TEMPERATURE}F and {ClientContext.MAXIMUM_COOLING_TEMPERATURE}F"
                )
        if heat_hold_temp is not None:
            if not isinstance(heat_hold_temp, numbers.Real):
                raise TypeError(f"heat_hold_temp must be an instance of {numbers.Real}")
            if not (
                ClientContext.MINIMUM_HEATING_TEMPERATURE
                <= float(heat_hold_temp)
                <= ClientContext.MAXIMUM_HEATING_TEMPERATURE
            ):
                raise ValueError(
                    f"heat_hold_temp must be between {ClientContext.MINIMUM_HEATING_TEMPERATURE}F and {ClientContext.MAXIMUM_HEATING_TEMPERATURE}F"
                )
        if fan_mode is not None and not isinstance(fan_mode, FanMode):
            raise TypeError(f"fan_mode must be an instance of {FanMode}")
        if hold_climate_ref is not None and not isinstance(hold_climate_ref, str):
            raise TypeError(f"hold_climate_ref must be an instance of {str}")
        if (
            cool_hold_temp is None
            and heat_hold_temp is None
            and hold_climate_ref is None
        ):
            raise ValueError(
                "cool_hold_temp, heat_hold_temp, and hold_climate_ref must not all "
                "be None. Either cool_hold_temp and heat_hold_temp must not be None "
                "or hold_climate_ref must not be None"
            )
        if hold_climate_ref is None and (
            cool_hold_temp is None or heat_hold_temp is None
        ):
            raise ValueError(
                "hold_climate_ref is None. cool_hold_temp and heat_hold_temp must "
                "not be None."
            )
        if start_date_time is not None:
            if not isinstance(start_date_time, DateTime):
                raise TypeError(f"start_date_time must be an instance of {DateTime}")
            if start_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "start_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if start_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "start_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if end_date_time is not None:
            if not isinstance(end_date_time, DateTime):
                raise TypeError(f"end_date_time must be an instance of {DateTime}")
            if end_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "end_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if end_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "end_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if (
            start_date_time is not None
            and end_date_time is not None
            and start_date_time >= end_date_time
        ):
            raise ValueError("end_date_time must be later than start_date_time")
        if not isinstance(hold_type, HoldType):
            raise TypeError(f"hold_type must be an instance of {HoldType}")
        if hold_type == HoldType.DATE_TIME and end_date_time is None:
            raise ValueError(
                f"hold_type is {HoldType.DATE_TIME.value}. end_date_time must not be None"
            )
        if hold_hours is not None and not isinstance(hold_hours, int):
            raise TypeError(f"hold_hours must be an instance of {int}")
        if hold_type == HoldType.HOLD_HOURS and hold_hours is None:
            raise ValueError(
                f"hold_type is {HoldType.HOLD_HOURS.value}. hold_hours must not be None"
            )
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        set_hold_parameters: dict[str, Any] = {"holdType": hold_type.value}

        if cool_hold_temp is not None:
            set_hold_parameters["coolHoldTemp"] = int(float(cool_hold_temp) * 10)

        if heat_hold_temp is not None:
            set_hold_parameters["heatHoldTemp"] = int(float(heat_hold_temp) * 10)

        if fan_mode is not None:
            set_hold_parameters["fan"] = fan_mode.value

        if hold_climate_ref is not None:
            set_hold_parameters["holdClimateRef"] = hold_climate_ref

        if start_date_time is not None:
            set_hold_parameters["startDate"] = (
                f"{start_date_time.year}-{start_date_time.month:02}-{start_date_time.day:02}"
            )
            set_hold_parameters["startTime"] = (
                f"{start_date_time.hour:02}:{start_date_time.minute:02}:{start_date_time.second:02}"
            )

        if end_date_time is not None:
            set_hold_parameters["endDate"] = (
                f"{end_date_time.year}-{end_date_time.month:02}-{end_date_time.day:02}"
            )
            set_hold_parameters["endTime"] = (
                f"{end_date_time.hour:02}:{end_date_time.minute:02}:{end_date_time.second:02}"
            )

        if hold_hours is not None:
            set_hold_parameters["holdHours"] = hold_hours

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[Function(type="setHold", params=set_hold_parameters)],
            timeout=timeout,
        )

    def set_occupied(
        self,
        occupied: bool,
        start_date_time: DateTime | None = None,
        end_date_time: DateTime | None = None,
        hold_type: HoldType = HoldType.INDEFINITE,
        hold_hours: int | None = None,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The set_occupied method may only be used by EMS thermostats. The
        method switches a thermostat from occupied mode to unoccupied,
        or vice versa. If used on a Smart thermostat, the method will
        throw an error. Switch occupancy events are treated as Holds.
        There may only be one Switch Occupancy at one time, and the new
        event will replace any previous event.

        Note that an occupancy event is created regardless what the
        program on the thermostat is set to. For example, if the program
        is currently unoccupied and you set occupied=False, an occupancy
        event will be created using the heat/cool settings of the
        unoccupied program climate. If your intent is to go back to the
        program and remove the occupancy event, use resumeProgram
        instead.

        :param occupied: The climate to use for the temperature,
        occupied (True) or unoccupied (False)
        :param start_date_time: The start date and time in thermostat
        time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time.
        Must be a timezone aware datetime
        :param hold_type: The hold duration type. Valid values:
        HoldType.DATE_TIME, HoldType.NEXT_TRANSITION,
        HoldType.INDEFINITE, and HoldType.HOLD_HOURS
        :param hold_hours: The number of hours to hold for, used and
        required if holdType='holdHours'
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If occupied is not a boolean, start_date_time
        is not a datetime, end_date_time is not a datetime, hold_type is
        not a member of HoldType, hold_hours is not an integer, or
        selection is not an instance of Selection
        :raises ValueError: If start/end date_times are earlier than
        2008-01-02 00:00:00 +0000, start/end date_times are later than
        2035-01-01 00:00:00 +0000, start_date_time is later than
        end_date_time, end_date_time is None while hold_type is
        HoldType.DATE_TIME, or hold_hours is None while hold_type is
        HoldType.HOLD_HOURS
        """
        if not isinstance(occupied, bool):
            raise TypeError(f"occupied must be an instance of {bool}")
        if start_date_time is not None:
            if not isinstance(start_date_time, DateTime):
                raise TypeError(f"start_date_time must be an instance of {DateTime}")
            if start_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "start_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if start_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "start_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if end_date_time is not None:
            if not isinstance(end_date_time, DateTime):
                raise TypeError(f"end_date_time must be an instance of {DateTime}")
            if end_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError(
                    "end_date_time must be later than {}".format(
                        ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
            if end_date_time > ClientContext.END_OF_TIME_DATE_TIME:
                raise ValueError(
                    "end_date_time must be earlier than {}".format(
                        ClientContext.END_OF_TIME_DATE_TIME.strftime(
                            "%Y-%m-%d %H:%M:%S %Z"
                        )
                    )
                )
        if (
            start_date_time is not None
            and end_date_time is not None
            and start_date_time >= end_date_time
        ):
            raise ValueError("end_date_time must be later than start_date_time")
        if not isinstance(hold_type, HoldType):
            raise TypeError(f"hold_type must be an instance of {HoldType}")
        if hold_type == HoldType.DATE_TIME and end_date_time is None:
            raise ValueError(
                f"hold_type is {HoldType.DATE_TIME.value}. end_date_time must not be None"
            )
        if hold_hours is not None and not isinstance(hold_hours, int):
            raise TypeError(f"hold_hours must be an instance of {int}")
        if hold_type == HoldType.HOLD_HOURS and hold_hours is None:
            raise ValueError(
                f"hold_type is {HoldType.HOLD_HOURS.value}. hold_hours must not be None"
            )
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        set_occupied_parameters: dict[str, Any] = {
            "occupied": occupied,
            "holdType": hold_type.value,
        }

        if start_date_time is not None:
            set_occupied_parameters["startDate"] = (
                f"{start_date_time.year}-{start_date_time.month:02}-{start_date_time.day:02}"
            )
            set_occupied_parameters["startTime"] = (
                f"{start_date_time.hour:02}:{start_date_time.minute:02}:{start_date_time.second:02}"
            )

        if end_date_time is not None:
            set_occupied_parameters["endDate"] = (
                f"{end_date_time.year}-{end_date_time.month:02}-{end_date_time.day:02}"
            )
            set_occupied_parameters["endTime"] = (
                f"{end_date_time.hour:02}:{end_date_time.minute:02}:{end_date_time.second:02}"
            )

        if hold_hours is not None:
            set_occupied_parameters["holdHours"] = hold_hours

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[Function(type="setOccupied", params=set_occupied_parameters)],
            timeout=timeout,
        )

    def unlink_voice_engine(
        self,
        engine_name: str,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The unlink voice engine function allows you to disable voice
        assistant for the selected thermostat.

        :param engine_name: The name of the engine to unlink
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If engine_name is not a string or selection
        is not an instance of Selection
        """
        if not isinstance(engine_name, str):
            raise TypeError(f"engine_name must be an instance of {str}")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[
                Function(type="unlinkVoiceEngine", params={"engineName": engine_name})
            ],
            timeout=timeout,
        )

    def update_sensor(
        self,
        name: str,
        device_id: str,
        sensor_id: str,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        """
        The update_sensor method allows the caller to update the name of
        an ecobee3 remote sensor. Each ecobee3 remote sensor "enclosure"
        contains two distinct sensors types temperature and occupancy.
        Only one of the sensors is required in the request. Both of the
        sensors' names will be updated to ensure consistency as they are
        part of the same remote sensor enclosure. This also reflects
        accurately what happens on the Thermostat itself.

        :param name: The updated name to give the sensor
        :param device_id: The device_id for the sensor, typically this
        indicates the enclosure and corresponds to the
        ThermostatRemoteSensor.id attribute
        :param sensor_id: The identifier for the sensor within the
        enclosure. Corresponds to the RemoteSensorCapability.id
        attribute
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the
        status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If name is not a string, device_id is not a
        string, sensor_id is not a string, or selection is not an
        instance of Selection
        :raises ValueError: If name has a length greater than 32
        """
        if not isinstance(name, str):
            raise TypeError(f"name must be an instance of {str}")
        if len(name) > 32:
            raise ValueError("name maximum length must not be greater than 32")
        if not isinstance(device_id, str):
            raise TypeError(f"device_id must be an instance of {str}")
        if not isinstance(sensor_id, str):
            raise TypeError(f"sensor_id must be an instance of {str}")
        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")

        return self.update_thermostats(
            selection,
            thermostat=None,
            functions=[
                Function(
                    type="updateSensor",
                    params={"name": name, "deviceId": device_id, "sensorId": sensor_id},
                )
            ],
            timeout=timeout,
        )
