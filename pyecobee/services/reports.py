import datetime
import json
import logging
from datetime import date
from datetime import datetime as DateTime

from pyecobee.enumerations import (
    SelectionType,
)
from pyecobee.objects.selection import Selection
from pyecobee.responses import (
    EcobeeCreateRuntimeReportJobResponse,
    EcobeeListRuntimeReportJobStatusResponse,
    EcobeeMeterReportsResponse,
    EcobeeRuntimeReportsResponse,
    EcobeeStatusResponse,
)
from pyecobee.services.context import ClientContext
from pyecobee.utilities import Utilities

logger = logging.getLogger(__name__)


class DomainComponent:
    """Base interface for an Ecobee API domain."""

    __slots__ = ("_context",)

    def __init__(self, context: ClientContext):
        self._context = context


class ReportsService(DomainComponent):
    def request_meter_reports(
        self, selection, start_date_time, end_date_time, meters="energy", timeout=5
    ):
        """
        The request_meter_reports method retrieves the historical meter
        reading information for a selection of thermostats.

        The report request is limited to retrieving information for up
        to 25 thermostats with a maximum period of 31 days, per request.
        The amount of data returned is considerable for 31 days of data
        for 25 thermostats (25 thermostats * 288 intervals per day * 31
        days = 223,200 rows of data).

        The data in the report is at 5 minute intervals for a whole day.
        The data represented in terms of runtime is for the 5 minute
        interval (up to 300 seconds).

        :param selection: The selection criteria for the request. Must
        have selection_type = 'thermostats' and selection_match = A CSV
        string of thermostat identifiers.
        :param start_date_time: The start date and time in thermostat
        time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time.
        Must be a timezone aware datetime
        :param meters: A CSV string of meter types. Only supported meter
        type is "energy"
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A MeterReportResponse object
        :rtype: EcobeeMeterReportsResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        start_date_time is not a datetime, end_date_time is not a
        datetime, or meters is not a string
        :raises ValueError: If selection.selection_type is not
        thermostats, selection specifies more than 25 thermostats,
        start/end date_times are earlier than 2008-01-02 00:00:00 +0000,
        start/end date_times are later than 2035-01-01 00:00:00 +0000,
        start_date_time is later than end_date_time, the duration
        between start_date_time and end_date_time is more than 31 days,
        meters is not a CSV string of "energy", or selection and meters
        don't have the same number of CSV entries
        """

        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if selection.selection_type != SelectionType.THERMOSTATS:
            raise ValueError(
                f"selection.selection_type must be set to {SelectionType.THERMOSTATS.value}"
            )
        if len(selection.selection_match.split(",")) > 25:
            raise ValueError("selection must not specify more than 25 thermostats")
        if not isinstance(start_date_time, DateTime):
            raise TypeError(f"start_date must be an instance of {DateTime}")
        if start_date_time.tzinfo is None or start_date_time.utcoffset() is None:
            raise ValueError("start_date_time must be timezone-aware")
        if start_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError(
                "start_date must be later than {}".format(
                    ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                )
            )
        if start_date_time > ClientContext.END_OF_TIME_DATE_TIME:
            raise ValueError(
                "start_date must be earlier than {}".format(
                    ClientContext.END_OF_TIME_DATE_TIME.strftime("%Y-%m-%d %H:%M:%S %Z")
                )
            )
        if not isinstance(end_date_time, DateTime):
            raise TypeError(f"end_date must be an instance of {DateTime}")
        if end_date_time.tzinfo is None or end_date_time.utcoffset() is None:
            raise ValueError("end_date_time must be timezone-aware")
        if end_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError(
                "end_date must be later than {}".format(
                    ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                )
            )
        if end_date_time > ClientContext.END_OF_TIME_DATE_TIME:
            raise ValueError(
                "end_date must be earlier than {}".format(
                    ClientContext.END_OF_TIME_DATE_TIME.strftime("%Y-%m-%d %H:%M:%S %Z")
                )
            )
        if start_date_time >= end_date_time:
            raise ValueError("end_date_time must be later than start_date_time")
        if (end_date_time - start_date_time).days > 31:
            raise ValueError(
                "Duration between start_date_time and end_date_time must not be more "
                "than 31 days"
            )
        if not isinstance(meters, str):
            raise TypeError(f"meters must be an instance of {str}")
        if not all(meter == "energy" for meter in meters.split(",")):
            raise ValueError('meters must be a CSV string of "energy"')
        if len(selection.selection_match.split(",")) != len(meters.split(",")):
            raise ValueError(
                "selection and meters must have the same number of CSV entries"
            )

        utc = datetime.UTC
        start_date_time = start_date_time.astimezone(utc)
        end_date_time = end_date_time.astimezone(utc)

        dictionary = {
            "selection": Utilities.object_to_dictionary(selection, type(selection)),
            "startDate": f"{start_date_time.year}-{start_date_time.month:02}-{start_date_time.day:02}",
            "startInterval": (start_date_time.hour * 12)
            + (start_date_time.minute // 5),
            "endDate": f"{end_date_time.year}-{end_date_time.month:02}-{end_date_time.day:02}",
            "endInterval": end_date_time.hour * 12 + (end_date_time.minute // 5),
            "meters": meters,
        }

        response = self._context._transport.request(
            "get",
            ClientContext.METER_REPORT_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeMeterReportsResponse)

    def request_runtime_reports(
        self,
        selection,
        start_date_time,
        end_date_time,
        columns,
        include_sensors=False,
        timeout=5,
    ):
        """
        The request_runtime_reports request is limited to retrieving
        information for up to 25 thermostats with a maximum period of 31
        days, per request. The amount of data returned is considerable
        for 31 days of data for 25 thermostats (25 thermostats * 288
        intervals per day * 31 days = 223,200 rows of data).

        The data in the report is at 5 minute intervals for a whole day.
        The data represented in terms of runtime is for the 5 minute
        interval (up to 300 seconds).

        :param selection: The selection criteria for the request. Must
        have selection_type = 'thermostats' and selection_match = A CSV
        string of thermostat identifiers.
        :param start_date_time: The start date and time in thermostat
        time. Must be a timezone aware datetime.
        :param end_date_time: The end date and time in thermostat time.
        Must be a timezone aware datetime
        :param columns: A CSV string of column names
        :param include_sensors: Whether to include sensor runtime report
        data for those thermostats which have it. Default: False
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A RuntimeReportResponse object
        :rtype: EcobeeRuntimeReportsResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        start_date_time is not a datetime, end_date_time is not a
        datetime, columns is not a string, or include_sensors is not a
        boolean
        :raises ValueError: If selection.selection_type is not
        "thermostats", selection specifies more than 25 thermostats,
        start/end date_times are earlier than 2008-01-02 00:00:00 +0000,
        start/end date_times are later than 2035-01-01 00:00:00 +0000,
        start_date_time is later than end_date_time, or the duration
        between start_date_time and end_date_time is more than 31 days
        """

        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if selection.selection_type != SelectionType.THERMOSTATS:
            raise ValueError(
                f"selection.selection_type must be set to {SelectionType.THERMOSTATS.value}"
            )
        if len(selection.selection_match.split(",")) > 25:
            raise ValueError("selection must not specify more than 25 thermostats")
        if not isinstance(start_date_time, DateTime):
            raise TypeError(f"start_date must be an instance of {DateTime}")
        if start_date_time.tzinfo is None or start_date_time.utcoffset() is None:
            raise ValueError("start_date_time must be timezone-aware")
        if start_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError(
                "start_date must be later than {}".format(
                    ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                )
            )
        if start_date_time > ClientContext.END_OF_TIME_DATE_TIME:
            raise ValueError(
                "start_date must be earlier than {}".format(
                    ClientContext.END_OF_TIME_DATE_TIME.strftime("%Y-%m-%d %H:%M:%S %Z")
                )
            )
        if not isinstance(end_date_time, DateTime):
            raise TypeError(f"end_date must be an instance of {DateTime}")
        if end_date_time.tzinfo is None or end_date_time.utcoffset() is None:
            raise ValueError("end_date_time must be timezone-aware")
        if end_date_time < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError(
                "end_date must be later than {}".format(
                    ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                )
            )
        if end_date_time > ClientContext.END_OF_TIME_DATE_TIME:
            raise ValueError(
                "end_date must be earlier than {}".format(
                    ClientContext.END_OF_TIME_DATE_TIME.strftime("%Y-%m-%d %H:%M:%S %Z")
                )
            )
        if start_date_time >= end_date_time:
            raise ValueError("end_date_time must be later than start_date_time")
        if (end_date_time - start_date_time).days > 31:
            raise ValueError(
                "Duration between start_date_time and end_date_time must not be more "
                "than 31 days"
            )
        if not isinstance(columns, str):
            raise TypeError(f"columns must be an instance of {str}")
        if not isinstance(include_sensors, bool):
            raise TypeError(f"include_sensors must be an instance of {bool}")

        utc = datetime.UTC
        start_date_time = start_date_time.astimezone(utc)
        end_date_time = end_date_time.astimezone(utc)

        dictionary = {
            "selection": Utilities.object_to_dictionary(selection, type(selection)),
            "startDate": f"{start_date_time.year}-{start_date_time.month:02}-{start_date_time.day:02}",
            "startInterval": (start_date_time.hour * 12)
            + (start_date_time.minute // 5),
            "endDate": f"{end_date_time.year}-{end_date_time.month:02}-{end_date_time.day:02}",
            "endInterval": end_date_time.hour * 12 + (end_date_time.minute // 5),
            "columns": columns,
            "includeSensors": include_sensors,
        }

        response = self._context._transport.request(
            "get",
            ClientContext.RUNTIME_REPORT_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeRuntimeReportsResponse)

    def create_runtime_report_job(
        self, selection, start_date, end_date, columns, include_sensors=False, timeout=5
    ):
        """
        The create_runtime_report_job method creates a new runtime
        report job to be processed. Reports can only be processed for
        thermostats associated with the user carrying out the request.
        If a user's queue limit has been reached, please either wait for
        the current job to be processed or cancel it and create a new
        job.

        :param selection: The selection criteria for the request. Must
        have selection_type = 'thermostats' or 'managementSet'
        :param start_date: The report start date
        :param end_date: The report end date
        :param columns: A CSV string of column names
        :param include_sensors: Whether to include sensor runtime report
        data for those thermostats which have it. Default: False
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A CreateRuntimeReportResponse object
        :rtype: EcobeeCreateRuntimeReportJobResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If selection is not an instance of Selection,
        start_date is not a date, end_date is not a date, columns is not
        a string, or include_sensors is not a boolean
        :raises ValueError: If start/end date are earlier than
        2008-01-02, start/end date_times are later than 2035-01-01, or
        start_date is later than end_date
        """

        if not isinstance(selection, Selection):
            raise TypeError(f"selection must be an instance of {Selection}")
        if (
            selection.selection_type != SelectionType.MANAGEMENT_SET
            and selection.selection_type != SelectionType.THERMOSTATS
        ):
            raise ValueError(
                f"selection.selection_type must be set to {SelectionType.MANAGEMENT_SET.value} or {SelectionType.THERMOSTATS.value}"
            )
        if not isinstance(start_date, date):
            raise TypeError(f"start_date must be an instance of {date}")
        if (
            DateTime(
                start_date.year,
                start_date.month,
                start_date.day,
                0,
                0,
                0,
                tzinfo=datetime.UTC,
            )
            < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME
        ):
            raise ValueError(
                "start_date must be later than {}".format(
                    ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                )
            )
        if (
            DateTime(
                start_date.year,
                start_date.month,
                start_date.day,
                0,
                0,
                0,
                tzinfo=datetime.UTC,
            )
            > ClientContext.END_OF_TIME_DATE_TIME
        ):
            raise ValueError(
                "start_date must be earlier than {}".format(
                    ClientContext.END_OF_TIME_DATE_TIME.strftime("%Y-%m-%d %H:%M:%S %Z")
                )
            )
        if not isinstance(end_date, date):
            raise TypeError(f"end_date must be an instance of {date}")
        if (
            DateTime(
                end_date.year,
                end_date.month,
                end_date.day,
                0,
                0,
                0,
                tzinfo=datetime.UTC,
            )
            < ClientContext.BEFORE_TIME_BEGAN_DATE_TIME
        ):
            raise ValueError(
                "end_date must be later than {}".format(
                    ClientContext.BEFORE_TIME_BEGAN_DATE_TIME.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                )
            )
        if (
            DateTime(
                end_date.year,
                end_date.month,
                end_date.day,
                0,
                0,
                0,
                tzinfo=datetime.UTC,
            )
            > ClientContext.END_OF_TIME_DATE_TIME
        ):
            raise ValueError(
                "end_date must be earlier than {}".format(
                    ClientContext.END_OF_TIME_DATE_TIME.strftime("%Y-%m-%d %H:%M:%S %Z")
                )
            )
        if start_date >= end_date:
            raise ValueError("end_date must be later than start_date")
        if not isinstance(columns, str):
            raise TypeError(f"columns must be an instance of {str}")
        if not isinstance(include_sensors, bool):
            raise TypeError(f"include_sensors must be an instance of {bool}")

        dictionary = {
            "selection": Utilities.object_to_dictionary(selection, type(selection)),
            "startDate": f"{start_date.year}-{start_date.month:02}-{start_date.day:02}",
            "endDate": f"{end_date.year}-{end_date.month:02}-{end_date.day:02}",
            "columns": columns,
            "includeSensors": include_sensors,
        }

        response = self._context._transport.request(
            "post",
            f"{ClientContext.RUNTIME_REPORT_JOB_URL}/create",
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(
            response, EcobeeCreateRuntimeReportJobResponse
        )

    def list_runtime_report_job_status(self, job_id=None, timeout=5):
        """
        The list_runtime_report_job_status method gets the status of the
        job for the given id or all current job statuses for the account
        carrying out the request.

        :param job_id: The id of the report job to get the status
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A ListRuntimeReportJobStatusResponse object
        :rtype: EcobeeListRuntimeReportJobStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If job_id is not a string
        """

        if job_id is not None:
            if not isinstance(job_id, str):
                raise TypeError(f"job_id must be an instance of {str}")

        dictionary = {}

        if job_id is not None:
            dictionary["jobId"] = job_id

        response = self._context._transport.request(
            "post",
            f"{ClientContext.RUNTIME_REPORT_JOB_URL}/status",
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return Utilities.process_http_response(
            response, EcobeeListRuntimeReportJobStatusResponse
        )

    def cancel_runtime_report_job(self, job_id, timeout=5):
        """
        The cancel_runtime_report_job method cancels any queued report
        job to avoid getting processed and to allow for queuing
        additional report jobs. A job that is already being processed
        will be completed, even if a request has been made to cancel it.

        :param job_id: The id of the report job to cancel
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If job_id is not a string
        """

        if not isinstance(job_id, str):
            raise TypeError(f"job_id must be an instance of {str}")

        dictionary = {"jobId": job_id}

        response = self._context._transport.request(
            "post",
            f"{ClientContext.RUNTIME_REPORT_JOB_URL}/cancel",
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)
