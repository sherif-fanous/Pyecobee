"""Shared state used by the domain service components."""

import datetime
from datetime import datetime as DateTime
from datetime import timedelta

from pyecobee.enumerations import Scope
from pyecobee.transport import HttpTransport


class ClientContext:
    """Transport and authentication state shared by domain components."""

    __slots__ = (
        "_thermostat_name",
        "_application_key",
        "_authorization_token",
        "_access_token",
        "_refresh_token",
        "_access_token_expires_on",
        "_refresh_token_expires_on",
        "_scope",
        "_transport",
    )

    AUTHORIZE_URL = "https://api.ecobee.com/authorize"
    TOKENS_URL = "https://api.ecobee.com/token"
    THERMOSTAT_SUMMARY_URL = "https://api.ecobee.com/1/thermostatSummary"
    THERMOSTAT_URL = "https://api.ecobee.com/1/thermostat"
    METER_REPORT_URL = "https://api.ecobee.com/1/meterReport"
    RUNTIME_REPORT_URL = "https://api.ecobee.com/1/runtimeReport"
    GROUP_URL = "https://api.ecobee.com/1/group"
    HIERARCHY_SET_URL = "https://api.ecobee.com/1/hierarchy/set"
    HIERARCHY_USER_URL = "https://api.ecobee.com/1/hierarchy/user"
    HIERARCHY_THERMOSTAT_URL = "https://api.ecobee.com/1/hierarchy/thermostat"
    DEMAND_RESPONSE_URL = "https://api.ecobee.com/1/demandResponse"
    DEMAND_MANAGEMENT_URL = "https://api.ecobee.com/1/demandManagement"
    RUNTIME_REPORT_JOB_URL = "https://api.ecobee.com/1/runtimeReportJob"

    BEFORE_TIME_BEGAN_DATE_TIME = DateTime(2008, 1, 2, 0, 0, tzinfo=datetime.UTC)
    END_OF_TIME_DATE_TIME = DateTime(2035, 1, 1, 0, 0, tzinfo=datetime.UTC)

    REFRESH_TOKEN_LIFETIME = timedelta(days=30)
    MINIMUM_COOLING_TEMPERATURE = -10.0
    MAXIMUM_COOLING_TEMPERATURE = 120.0
    MINIMUM_HEATING_TEMPERATURE = 45.0
    MAXIMUM_HEATING_TEMPERATURE = 120.0

    def __init__(
        self,
        thermostat_name,
        application_key,
        authorization_token=None,
        access_token=None,
        refresh_token=None,
        access_token_expires_on=None,
        refresh_token_expires_on=None,
        scope=Scope.SMART_WRITE,
    ):
        self._thermostat_name = thermostat_name
        self._application_key = application_key
        self._authorization_token = authorization_token
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._access_token_expires_on = access_token_expires_on
        self._refresh_token_expires_on = refresh_token_expires_on
        self._scope = scope
        self._transport = HttpTransport()
