import logging

from pyecobee.ecobee_object import EcobeeObject
from pyecobee.enumerations import (
    FanMode,
    HoldType,
    Scope,
    SelectionType,
)
from pyecobee.objects.selection import Selection
from pyecobee.services import (
    AuthorizationService,
    DemandService,
    GroupsService,
    HierarchyService,
    ReportsService,
    ThermostatsService,
)
from pyecobee.services.context import ClientContext

logger = logging.getLogger(__name__)


class EcobeeService(EcobeeObject):
    """Compatibility facade delegating API operations to domain components."""

    __slots__ = (
        "_context",
        "_authorization",
        "_thermostats",
        "_groups",
        "_hierarchy",
        "_demand",
        "_reports",
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

    attribute_name_map = {
        "thermostat_name": "thermostat_name",
        "application_key": "application_key",
        "authorization_token": "authorization_token",
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "access_token_expires_on": "access_token_expires_on",
        "refresh_token_expires_on": "refresh_token_expires_on",
        "scope": "scope",
    }
    attribute_type_map = {
        "thermostat_name": "str",
        "application_key": "str",
        "authorization_token": "str",
        "access_token": "str",
        "refresh_token": "str",
        "access_token_expires_on": "datetime",
        "refresh_token_expires_on": "datetime",
        "scope": "Scope",
    }

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
        """
        Construct an EcobeeService instance

        :param thermostat_name: Name of the thermostat
        :param application_key: The unique application key for your
        application
        :param authorization_token: Credentials to be used to retrieve
        the initial access_token and refresh_token
        :param access_token: Credentials to be used in all requests
        :param refresh_token: Credentials to be used to refresh
        access_token and refresh_token
        :param access_token_expires_on: When the access token expires on
        in UTC time
        :param refresh_token_expires_on: When the refresh token expires
        on in UTC time
        :param scope: Scope the application requests from the user.
        Valid values: Scope.SMART_READ, Scope.SMART_WRITE, and Scope.EMS
        """
        if not isinstance(application_key, str):
            raise TypeError(f"application_key must be an instance of {str}")
        if len(application_key) != 32:
            raise ValueError("application_key must be a 32 alphanumeric string")

        self._context = ClientContext(
            thermostat_name,
            application_key,
            authorization_token,
            access_token,
            refresh_token,
            access_token_expires_on,
            refresh_token_expires_on,
            scope,
        )
        self._authorization = AuthorizationService(self._context)
        self._thermostats = ThermostatsService(self._context)
        self._groups = GroupsService(self._context)
        self._hierarchy = HierarchyService(self._context)
        self._demand = DemandService(self._context)
        self._reports = ReportsService(self._context)

    def authorize(self, response_type="ecobeePin", timeout=5):
        return self._authorization.authorize(
            response_type=response_type, timeout=timeout
        )

    def request_tokens(self, grant_type="ecobeePin", timeout=5):
        return self._authorization.request_tokens(
            grant_type=grant_type, timeout=timeout
        )

    def refresh_tokens(self, grant_type="refresh_token", timeout=5):
        return self._authorization.refresh_tokens(
            grant_type=grant_type, timeout=timeout
        )

    def request_thermostats_summary(self, selection, timeout=5):
        return self._thermostats.request_thermostats_summary(
            selection=selection, timeout=timeout
        )

    def request_thermostats(self, selection, timeout=5):
        return self._thermostats.request_thermostats(
            selection=selection, timeout=timeout
        )

    def update_thermostats(self, selection, thermostat=None, functions=None, timeout=5):
        return self._thermostats.update_thermostats(
            selection=selection,
            thermostat=thermostat,
            functions=functions,
            timeout=timeout,
        )

    def acknowledge(
        self,
        thermostat_identifier,
        ack_ref,
        ack_type,
        remind_me_later=False,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
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
        plug_name,
        plug_state,
        start_date_time=None,
        end_date_time=None,
        hold_type=HoldType.INDEFINITE,
        hold_hours=None,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
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
        name,
        cool_hold_temp,
        heat_hold_temp,
        start_date_time=None,
        end_date_time=None,
        fan_mode=FanMode.AUTO,
        fan_min_on_time=0,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
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
        name,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
        return self._thermostats.delete_vacation(
            name=name, selection=selection, timeout=timeout
        )

    def reset_preferences(
        self,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
        return self._thermostats.reset_preferences(selection=selection, timeout=timeout)

    def resume_program(
        self,
        resume_all=False,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
        return self._thermostats.resume_program(
            resume_all=resume_all, selection=selection, timeout=timeout
        )

    def send_message(
        self,
        text,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
        return self._thermostats.send_message(
            text=text, selection=selection, timeout=timeout
        )

    def set_hold(
        self,
        cool_hold_temp=None,
        heat_hold_temp=None,
        fan_mode=None,
        hold_climate_ref=None,
        start_date_time=None,
        end_date_time=None,
        hold_type=HoldType.INDEFINITE,
        hold_hours=None,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
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
        occupied,
        start_date_time=None,
        end_date_time=None,
        hold_type=HoldType.INDEFINITE,
        hold_hours=None,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
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
        engine_name,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
        return self._thermostats.unlink_voice_engine(
            engine_name=engine_name, selection=selection, timeout=timeout
        )

    def update_sensor(
        self,
        name,
        device_id,
        sensor_id,
        selection=Selection(
            selection_type=SelectionType.REGISTERED.value, selection_match=""
        ),
        timeout=5,
    ):
        return self._thermostats.update_sensor(
            name=name,
            device_id=device_id,
            sensor_id=sensor_id,
            selection=selection,
            timeout=timeout,
        )

    def request_groups(self, selection, timeout=5):
        return self._groups.request_groups(selection=selection, timeout=timeout)

    def update_groups(self, selection, groups, timeout=5):
        return self._groups.update_groups(
            selection=selection, groups=groups, timeout=timeout
        )

    def list_hierarchy_sets(
        self,
        set_path,
        recursive=False,
        include_privileges=False,
        include_thermostats=False,
        timeout=5,
    ):
        return self._hierarchy.list_hierarchy_sets(
            set_path=set_path,
            recursive=recursive,
            include_privileges=include_privileges,
            include_thermostats=include_thermostats,
            timeout=timeout,
        )

    def list_hierarchy_users(
        self, set_path, recursive=False, include_privileges=False, timeout=5
    ):
        return self._hierarchy.list_hierarchy_users(
            set_path=set_path,
            recursive=recursive,
            include_privileges=include_privileges,
            timeout=timeout,
        )

    def add_hierarchy_set(self, set_name, parent_path, timeout=5):
        return self._hierarchy.add_hierarchy_set(
            set_name=set_name, parent_path=parent_path, timeout=timeout
        )

    def remove_hierarchy_set(self, set_path, timeout=5):
        return self._hierarchy.remove_hierarchy_set(set_path=set_path, timeout=timeout)

    def rename_hierarchy_set(self, set_path, new_name, timeout=5):
        return self._hierarchy.rename_hierarchy_set(
            set_path=set_path, new_name=new_name, timeout=timeout
        )

    def move_hierarchy_set(self, set_path, to_path, timeout=5):
        return self._hierarchy.move_hierarchy_set(
            set_path=set_path, to_path=to_path, timeout=timeout
        )

    def add_hierarchy_users(self, users, privileges=None, timeout=5):
        return self._hierarchy.add_hierarchy_users(
            users=users, privileges=privileges, timeout=timeout
        )

    def remove_hierarchy_users(self, set_path, users, timeout=5):
        return self._hierarchy.remove_hierarchy_users(
            set_path=set_path, users=users, timeout=timeout
        )

    def unregister_hierarchy_users(self, users, timeout=5):
        return self._hierarchy.unregister_hierarchy_users(users=users, timeout=timeout)

    def update_hierarchy_users(self, users=None, privileges=None, timeout=5):
        return self._hierarchy.update_hierarchy_users(
            users=users, privileges=privileges, timeout=timeout
        )

    def register_hierarchy_thermostats(self, thermostats, set_path=None, timeout=5):
        return self._hierarchy.register_hierarchy_thermostats(
            thermostats=thermostats, set_path=set_path, timeout=timeout
        )

    def unregister_hierarchy_thermostats(self, thermostats, timeout=5):
        return self._hierarchy.unregister_hierarchy_thermostats(
            thermostats=thermostats, timeout=timeout
        )

    def move_hierarchy_thermostats(
        self, set_path, to_path, thermostats=None, timeout=5
    ):
        return self._hierarchy.move_hierarchy_thermostats(
            set_path=set_path, to_path=to_path, thermostats=thermostats, timeout=timeout
        )

    def assign_hierarchy_thermostats(self, set_path, thermostats, timeout=5):
        return self._hierarchy.assign_hierarchy_thermostats(
            set_path=set_path, thermostats=thermostats, timeout=timeout
        )

    def list_demand_responses(self, timeout=5):
        return self._demand.list_demand_responses(timeout=timeout)

    def issue_demand_response(self, selection, demand_response, timeout=5):
        return self._demand.issue_demand_response(
            selection=selection, demand_response=demand_response, timeout=timeout
        )

    def cancel_demand_response(self, demand_response_ref, timeout=5):
        return self._demand.cancel_demand_response(
            demand_response_ref=demand_response_ref, timeout=timeout
        )

    def issue_demand_managements(self, selection, demand_managements, timeout=5):
        return self._demand.issue_demand_managements(
            selection=selection, demand_managements=demand_managements, timeout=timeout
        )

    def request_meter_reports(
        self, selection, start_date_time, end_date_time, meters="energy", timeout=5
    ):
        return self._reports.request_meter_reports(
            selection=selection,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            meters=meters,
            timeout=timeout,
        )

    def request_runtime_reports(
        self,
        selection,
        start_date_time,
        end_date_time,
        columns,
        include_sensors=False,
        timeout=5,
    ):
        return self._reports.request_runtime_reports(
            selection=selection,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            columns=columns,
            include_sensors=include_sensors,
            timeout=timeout,
        )

    def create_runtime_report_job(
        self, selection, start_date, end_date, columns, include_sensors=False, timeout=5
    ):
        return self._reports.create_runtime_report_job(
            selection=selection,
            start_date=start_date,
            end_date=end_date,
            columns=columns,
            include_sensors=include_sensors,
            timeout=timeout,
        )

    def list_runtime_report_job_status(self, job_id=None, timeout=5):
        return self._reports.list_runtime_report_job_status(
            job_id=job_id, timeout=timeout
        )

    def cancel_runtime_report_job(self, job_id, timeout=5):
        return self._reports.cancel_runtime_report_job(job_id=job_id, timeout=timeout)

    @property
    def thermostat_name(self):
        return self._context._thermostat_name

    @property
    def application_key(self):
        return self._context._application_key

    @application_key.setter
    def application_key(self, application_key):
        self._context._application_key = application_key

    @property
    def authorization_token(self):
        return self._context._authorization_token

    @authorization_token.setter
    def authorization_token(self, authorization_token):
        self._context._authorization_token = authorization_token

    @property
    def access_token(self):
        return self._context._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._context._access_token = access_token

    @property
    def refresh_token(self):
        return self._context._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        self._context._refresh_token = refresh_token

    @property
    def access_token_expires_on(self):
        return self._context._access_token_expires_on

    @access_token_expires_on.setter
    def access_token_expires_on(self, access_token_expires_on):
        self._context._access_token_expires_on = access_token_expires_on

    @property
    def refresh_token_expires_on(self):
        return self._context._refresh_token_expires_on

    @refresh_token_expires_on.setter
    def refresh_token_expires_on(self, refresh_token_expires_on):
        self._context._refresh_token_expires_on = refresh_token_expires_on

    @property
    def scope(self):
        return self._context._scope
