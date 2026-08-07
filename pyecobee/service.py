import logging
from collections.abc import Callable
from datetime import date
from datetime import datetime as DateTime
from typing import Any

from pyecobee.enumerations import (
    AckType,
    FanMode,
    HoldType,
    PlugState,
    Scope,
    SelectionType,
)
from pyecobee.objects.demand_management import DemandManagement
from pyecobee.objects.demand_response import DemandResponse
from pyecobee.objects.function import Function
from pyecobee.objects.group import Group
from pyecobee.objects.hierarchy_privilege import HierarchyPrivilege
from pyecobee.objects.hierarchy_user import HierarchyUser
from pyecobee.objects.selection import Selection
from pyecobee.objects.thermostat import Thermostat
from pyecobee.responses import (
    EcobeeAuthorizeResponse,
    EcobeeCreateRuntimeReportJobResponse,
    EcobeeGroupsResponse,
    EcobeeIssueDemandResponsesResponse,
    EcobeeListDemandResponsesResponse,
    EcobeeListHierarchySetsResponse,
    EcobeeListHierarchyUsersResponse,
    EcobeeListRuntimeReportJobStatusResponse,
    EcobeeMeterReportsResponse,
    EcobeeRuntimeReportsResponse,
    EcobeeStatusResponse,
    EcobeeThermostatResponse,
    EcobeeThermostatsSummaryResponse,
    EcobeeTokensResponse,
)
from pyecobee.services import (
    AuthorizationService,
    DemandService,
    GroupsService,
    HierarchyService,
    ReportsService,
    ThermostatsService,
)
from pyecobee.services.context import ClientContext
from pyecobee.tokens import Tokens

logger = logging.getLogger(__name__)


class EcobeeService:
    """Compatibility facade delegating API operations to domain components."""

    __slots__ = (
        "_authorization",
        "_context",
        "_demand",
        "_groups",
        "_hierarchy",
        "_reports",
        "_thermostats",
    )

    AUTHORIZE_URL = ClientContext.AUTHORIZE_URL
    TOKENS_URL = ClientContext.TOKENS_URL
    THERMOSTAT_SUMMARY_URL = ClientContext.THERMOSTAT_SUMMARY_URL
    THERMOSTAT_URL = ClientContext.THERMOSTAT_URL
    METER_REPORT_URL = ClientContext.METER_REPORT_URL
    RUNTIME_REPORT_URL = ClientContext.RUNTIME_REPORT_URL
    GROUP_URL = ClientContext.GROUP_URL
    HIERARCHY_SET_URL = ClientContext.HIERARCHY_SET_URL
    HIERARCHY_USER_URL = ClientContext.HIERARCHY_USER_URL
    HIERARCHY_THERMOSTAT_URL = ClientContext.HIERARCHY_THERMOSTAT_URL
    DEMAND_RESPONSE_URL = ClientContext.DEMAND_RESPONSE_URL
    DEMAND_MANAGEMENT_URL = ClientContext.DEMAND_MANAGEMENT_URL
    RUNTIME_REPORT_JOB_URL = ClientContext.RUNTIME_REPORT_JOB_URL
    BEFORE_TIME_BEGAN_DATE_TIME = ClientContext.BEFORE_TIME_BEGAN_DATE_TIME
    END_OF_TIME_DATE_TIME = ClientContext.END_OF_TIME_DATE_TIME
    MINIMUM_COOLING_TEMPERATURE = ClientContext.MINIMUM_COOLING_TEMPERATURE
    MAXIMUM_COOLING_TEMPERATURE = ClientContext.MAXIMUM_COOLING_TEMPERATURE
    MINIMUM_HEATING_TEMPERATURE = ClientContext.MINIMUM_HEATING_TEMPERATURE
    MAXIMUM_HEATING_TEMPERATURE = ClientContext.MAXIMUM_HEATING_TEMPERATURE

    def __init__(
        self,
        thermostat_name: str,
        application_key: str,
        tokens: Tokens | dict[str, Any],
        on_tokens_changed: Callable[[Tokens], object],
    ) -> None:
        """
        Construct an EcobeeService instance

        :param thermostat_name: Name of the thermostat
        :param application_key: The unique application key for your
        application
        :param tokens: The credentials held for this application, as a
        Tokens instance or a mapping produced by Tokens.to_dict(). Pass
        Tokens() when authorizing for the first time, optionally with the
        scope to request
        :param on_tokens_changed: Callable invoked with a Tokens instance
        whenever new credentials are issued, whether by authorize,
        request_tokens, refresh_tokens or an automatic renewal. It is
        required because ecobee replaces the refresh token every time it
        issues one, so credentials that are not stored are lost. Pass a
        callable that discards its argument to opt out
        :raises TypeError: If application_key is not a string, tokens is
        neither a Tokens instance nor a mapping, or on_tokens_changed is
        not callable
        :raises ValueError: If application_key is not 32 characters
        """
        if not isinstance(application_key, str):
            raise TypeError(f"application_key must be an instance of {str}")
        if len(application_key) != 32:
            raise ValueError("application_key must be a 32 alphanumeric string")
        if isinstance(tokens, dict):
            tokens = Tokens.from_dict(tokens)
        if not isinstance(tokens, Tokens):
            raise TypeError(f"tokens must be an instance of {Tokens} or {dict}")
        if not callable(on_tokens_changed):
            raise TypeError("on_tokens_changed must be callable")

        self._context = ClientContext(
            thermostat_name, application_key, tokens, on_tokens_changed
        )
        self._authorization = AuthorizationService(self._context)
        self._thermostats = ThermostatsService(self._context)
        self._groups = GroupsService(self._context)
        self._hierarchy = HierarchyService(self._context)
        self._demand = DemandService(self._context)
        self._reports = ReportsService(self._context)

    def authorize(
        self, response_type: str = "ecobeePin", timeout: float = 5
    ) -> EcobeeAuthorizeResponse:
        return self._authorization.authorize(
            response_type=response_type, timeout=timeout
        )

    def request_tokens(
        self, grant_type: str = "ecobeePin", timeout: float = 5
    ) -> EcobeeTokensResponse:
        return self._authorization.request_tokens(
            grant_type=grant_type, timeout=timeout
        )

    def refresh_tokens(
        self, grant_type: str = "refresh_token", timeout: float = 5
    ) -> EcobeeTokensResponse:
        return self._authorization.refresh_tokens(
            grant_type=grant_type, timeout=timeout
        )

    def request_thermostats_summary(
        self, selection: Selection, timeout: float = 5
    ) -> EcobeeThermostatsSummaryResponse:
        return self._thermostats.request_thermostats_summary(
            selection=selection, timeout=timeout
        )

    def request_thermostats(
        self, selection: Selection, timeout: float = 5
    ) -> EcobeeThermostatResponse:
        return self._thermostats.request_thermostats(
            selection=selection, timeout=timeout
        )

    def update_thermostats(
        self,
        selection: Selection,
        thermostat: Thermostat | None = None,
        functions: list[Function] | None = None,
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._thermostats.update_thermostats(
            selection=selection,
            thermostat=thermostat,
            functions=functions,
            timeout=timeout,
        )

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
        return self._thermostats.acknowledge(
            thermostat_identifier=thermostat_identifier,
            ack_ref=ack_ref,
            ack_type=ack_type,
            remind_me_later=remind_me_later,
            selection=selection,
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
        return self._thermostats.control_plug(
            plug_name=plug_name,
            plug_state=plug_state,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            hold_type=hold_type,
            hold_hours=hold_hours,
            selection=selection,
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
        return self._thermostats.create_vacation(
            name=name,
            cool_hold_temp=cool_hold_temp,
            heat_hold_temp=heat_hold_temp,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            fan_mode=fan_mode,
            fan_min_on_time=fan_min_on_time,
            selection=selection,
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
        return self._thermostats.delete_vacation(
            name=name, selection=selection, timeout=timeout
        )

    def reset_preferences(
        self,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._thermostats.reset_preferences(selection=selection, timeout=timeout)

    def resume_program(
        self,
        resume_all: bool = False,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._thermostats.resume_program(
            resume_all=resume_all, selection=selection, timeout=timeout
        )

    def send_message(
        self,
        text: str,
        selection: Selection = Selection(
            selection_type=SelectionType.REGISTERED, selection_match=""
        ),
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._thermostats.send_message(
            text=text, selection=selection, timeout=timeout
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
        return self._thermostats.set_hold(
            cool_hold_temp=cool_hold_temp,
            heat_hold_temp=heat_hold_temp,
            fan_mode=fan_mode,
            hold_climate_ref=hold_climate_ref,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            hold_type=hold_type,
            hold_hours=hold_hours,
            selection=selection,
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
        return self._thermostats.set_occupied(
            occupied=occupied,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            hold_type=hold_type,
            hold_hours=hold_hours,
            selection=selection,
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
        return self._thermostats.unlink_voice_engine(
            engine_name=engine_name, selection=selection, timeout=timeout
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
        return self._thermostats.update_sensor(
            name=name,
            device_id=device_id,
            sensor_id=sensor_id,
            selection=selection,
            timeout=timeout,
        )

    def request_groups(
        self, selection: Selection, timeout: float = 5
    ) -> EcobeeGroupsResponse:
        return self._groups.request_groups(selection=selection, timeout=timeout)

    def update_groups(
        self, selection: Selection, groups: list[Group], timeout: float = 5
    ) -> EcobeeGroupsResponse:
        return self._groups.update_groups(
            selection=selection, groups=groups, timeout=timeout
        )

    def list_hierarchy_sets(
        self,
        set_path: str,
        recursive: bool = False,
        include_privileges: bool = False,
        include_thermostats: bool = False,
        timeout: float = 5,
    ) -> EcobeeListHierarchySetsResponse:
        return self._hierarchy.list_hierarchy_sets(
            set_path=set_path,
            recursive=recursive,
            include_privileges=include_privileges,
            include_thermostats=include_thermostats,
            timeout=timeout,
        )

    def list_hierarchy_users(
        self,
        set_path: str,
        recursive: bool = False,
        include_privileges: bool = False,
        timeout: float = 5,
    ) -> EcobeeListHierarchyUsersResponse:
        return self._hierarchy.list_hierarchy_users(
            set_path=set_path,
            recursive=recursive,
            include_privileges=include_privileges,
            timeout=timeout,
        )

    def add_hierarchy_set(
        self, set_name: str, parent_path: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.add_hierarchy_set(
            set_name=set_name, parent_path=parent_path, timeout=timeout
        )

    def remove_hierarchy_set(
        self, set_path: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.remove_hierarchy_set(set_path=set_path, timeout=timeout)

    def rename_hierarchy_set(
        self, set_path: str, new_name: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.rename_hierarchy_set(
            set_path=set_path, new_name=new_name, timeout=timeout
        )

    def move_hierarchy_set(
        self, set_path: str, to_path: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.move_hierarchy_set(
            set_path=set_path, to_path=to_path, timeout=timeout
        )

    def add_hierarchy_users(
        self,
        users: list[HierarchyUser],
        privileges: list[HierarchyPrivilege] | None = None,
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._hierarchy.add_hierarchy_users(
            users=users, privileges=privileges, timeout=timeout
        )

    def remove_hierarchy_users(
        self, set_path: str, users: list[HierarchyUser], timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.remove_hierarchy_users(
            set_path=set_path, users=users, timeout=timeout
        )

    def unregister_hierarchy_users(
        self, users: list[HierarchyUser], timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.unregister_hierarchy_users(users=users, timeout=timeout)

    def update_hierarchy_users(
        self,
        users: list[HierarchyUser] | None = None,
        privileges: list[HierarchyPrivilege] | None = None,
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._hierarchy.update_hierarchy_users(
            users=users, privileges=privileges, timeout=timeout
        )

    def register_hierarchy_thermostats(
        self, thermostats: str, set_path: str | None = None, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.register_hierarchy_thermostats(
            thermostats=thermostats, set_path=set_path, timeout=timeout
        )

    def unregister_hierarchy_thermostats(
        self, thermostats: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.unregister_hierarchy_thermostats(
            thermostats=thermostats, timeout=timeout
        )

    def move_hierarchy_thermostats(
        self,
        set_path: str,
        to_path: str,
        thermostats: str | None = None,
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._hierarchy.move_hierarchy_thermostats(
            set_path=set_path, to_path=to_path, thermostats=thermostats, timeout=timeout
        )

    def assign_hierarchy_thermostats(
        self, set_path: str, thermostats: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._hierarchy.assign_hierarchy_thermostats(
            set_path=set_path, thermostats=thermostats, timeout=timeout
        )

    def list_demand_responses(
        self, timeout: float = 5
    ) -> EcobeeListDemandResponsesResponse:
        return self._demand.list_demand_responses(timeout=timeout)

    def issue_demand_response(
        self, selection: Selection, demand_response: DemandResponse, timeout: float = 5
    ) -> EcobeeIssueDemandResponsesResponse:
        return self._demand.issue_demand_response(
            selection=selection, demand_response=demand_response, timeout=timeout
        )

    def cancel_demand_response(
        self, demand_response_ref: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._demand.cancel_demand_response(
            demand_response_ref=demand_response_ref, timeout=timeout
        )

    def issue_demand_managements(
        self,
        selection: Selection,
        demand_managements: list[DemandManagement],
        timeout: float = 5,
    ) -> EcobeeStatusResponse:
        return self._demand.issue_demand_managements(
            selection=selection, demand_managements=demand_managements, timeout=timeout
        )

    def request_meter_reports(
        self,
        selection: Selection,
        start_date_time: DateTime,
        end_date_time: DateTime,
        meters: str = "energy",
        timeout: float = 5,
    ) -> EcobeeMeterReportsResponse:
        return self._reports.request_meter_reports(
            selection=selection,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            meters=meters,
            timeout=timeout,
        )

    def request_runtime_reports(
        self,
        selection: Selection,
        start_date_time: DateTime,
        end_date_time: DateTime,
        columns: str,
        include_sensors: bool = False,
        timeout: float = 5,
    ) -> EcobeeRuntimeReportsResponse:
        return self._reports.request_runtime_reports(
            selection=selection,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            columns=columns,
            include_sensors=include_sensors,
            timeout=timeout,
        )

    def create_runtime_report_job(
        self,
        selection: Selection,
        start_date: date,
        end_date: date,
        columns: str,
        include_sensors: bool = False,
        timeout: float = 5,
    ) -> EcobeeCreateRuntimeReportJobResponse:
        return self._reports.create_runtime_report_job(
            selection=selection,
            start_date=start_date,
            end_date=end_date,
            columns=columns,
            include_sensors=include_sensors,
            timeout=timeout,
        )

    def list_runtime_report_job_status(
        self, job_id: str | None = None, timeout: float = 5
    ) -> EcobeeListRuntimeReportJobStatusResponse:
        return self._reports.list_runtime_report_job_status(
            job_id=job_id, timeout=timeout
        )

    def cancel_runtime_report_job(
        self, job_id: str, timeout: float = 5
    ) -> EcobeeStatusResponse:
        return self._reports.cancel_runtime_report_job(job_id=job_id, timeout=timeout)

    @property
    def tokens(self) -> Tokens:
        """Return the credentials currently held."""
        return self._context.tokens

    @property
    def thermostat_name(self) -> str:
        return self._context.thermostat_name

    @property
    def application_key(self) -> str:
        return self._context.application_key

    @property
    def authorization_token(self) -> str | None:
        return self._context.tokens.authorization_token

    @property
    def access_token(self) -> str | None:
        return self._context.tokens.access_token

    @property
    def refresh_token(self) -> str | None:
        return self._context.tokens.refresh_token

    @property
    def access_token_expires_on(self) -> DateTime | None:
        return self._context.tokens.access_token_expires_on

    @property
    def refresh_token_expires_on(self) -> DateTime | None:
        return self._context.tokens.refresh_token_expires_on

    @property
    def scope(self) -> Scope:
        return self._context.tokens.scope
