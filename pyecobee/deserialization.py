"""Safe conversion of ecobee API payloads into response objects."""

import builtins
import keyword
import logging

from pyecobee.enumerations import (
    AckType,
    ActionType,
    ClimateType,
    DehumidifierMode,
    EquipmentStatus,
    EventType,
    ExtendedHvacMode,
    FanMode,
    HoldType,
    HouseStyle,
    HumidifierMode,
    HvacMode,
    OutputType,
    Owner,
    PlugState,
    RemoteSensorCapabilityType,
    RemoteSensorType,
    ReportJobStatus,
    Scope,
    SelectionType,
    SensorType,
    SensorUsage,
    StateType,
    ThermostatModelNumber,
    VentilatorMode,
)
from pyecobee.exceptions import EcobeeException
from pyecobee.objects.action import Action
from pyecobee.objects.alert import Alert
from pyecobee.objects.audio import Audio
from pyecobee.objects.climate import Climate
from pyecobee.objects.demand_management import DemandManagement
from pyecobee.objects.demand_response import DemandResponse
from pyecobee.objects.device import Device
from pyecobee.objects.electricity import Electricity
from pyecobee.objects.electricity_device import ElectricityDevice
from pyecobee.objects.electricity_tier import ElectricityTier
from pyecobee.objects.energy import Energy
from pyecobee.objects.equipment_setting import EquipmentSetting
from pyecobee.objects.event import Event
from pyecobee.objects.extended_runtime import ExtendedRuntime
from pyecobee.objects.function import Function
from pyecobee.objects.general_setting import GeneralSetting
from pyecobee.objects.group import Group
from pyecobee.objects.hierarchy_privilege import HierarchyPrivilege
from pyecobee.objects.hierarchy_set import HierarchySet
from pyecobee.objects.hierarchy_user import HierarchyUser
from pyecobee.objects.house_details import HouseDetails
from pyecobee.objects.limit_setting import LimitSetting
from pyecobee.objects.location import Location
from pyecobee.objects.management import Management
from pyecobee.objects.meter_report import MeterReport
from pyecobee.objects.meter_report_data import MeterReportData
from pyecobee.objects.notification_settings import NotificationSettings
from pyecobee.objects.output import Output
from pyecobee.objects.page import Page
from pyecobee.objects.program import Program
from pyecobee.objects.remote_sensor import RemoteSensor
from pyecobee.objects.remote_sensor_capability import RemoteSensorCapability
from pyecobee.objects.report_job import ReportJob
from pyecobee.objects.runtime import Runtime
from pyecobee.objects.runtime_report import RuntimeReport
from pyecobee.objects.runtime_sensor_metadata import RuntimeSensorMetadata
from pyecobee.objects.runtime_sensor_report import RuntimeSensorReport
from pyecobee.objects.security_settings import SecuritySettings
from pyecobee.objects.selection import Selection
from pyecobee.objects.sensor import Sensor
from pyecobee.objects.settings import Settings
from pyecobee.objects.state import State
from pyecobee.objects.status import Status
from pyecobee.objects.technician import Technician
from pyecobee.objects.thermostat import Thermostat
from pyecobee.objects.time_of_use import TimeOfUse
from pyecobee.objects.user import User
from pyecobee.objects.utility import Utility
from pyecobee.objects.version import Version
from pyecobee.objects.voice_engine import VoiceEngine
from pyecobee.objects.weather import Weather
from pyecobee.objects.weather_forecast import WeatherForecast
from pyecobee.responses import (
    EcobeeAuthorizeResponse,
    EcobeeCreateRuntimeReportJobResponse,
    EcobeeErrorResponse,
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

logger = logging.getLogger(__name__)


class EcobeeDeserializationException(EcobeeException):
    """Raised when a known ecobee response field cannot be converted."""


MODEL_REGISTRY = {
    model.__name__: model
    for model in (
        Action,
        Alert,
        Audio,
        Climate,
        DemandManagement,
        DemandResponse,
        Device,
        Electricity,
        ElectricityDevice,
        ElectricityTier,
        Energy,
        EquipmentSetting,
        Event,
        ExtendedRuntime,
        Function,
        GeneralSetting,
        Group,
        HierarchyPrivilege,
        HierarchySet,
        HierarchyUser,
        HouseDetails,
        LimitSetting,
        Location,
        Management,
        MeterReport,
        MeterReportData,
        NotificationSettings,
        Output,
        Page,
        Program,
        RemoteSensor,
        RemoteSensorCapability,
        ReportJob,
        Runtime,
        RuntimeReport,
        RuntimeSensorMetadata,
        RuntimeSensorReport,
        SecuritySettings,
        Selection,
        Sensor,
        Settings,
        State,
        Status,
        Technician,
        Thermostat,
        TimeOfUse,
        User,
        Utility,
        Version,
        VoiceEngine,
        Weather,
        WeatherForecast,
        EcobeeAuthorizeResponse,
        EcobeeCreateRuntimeReportJobResponse,
        EcobeeErrorResponse,
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
}

ENUM_REGISTRY = {
    enum.__name__: enum
    for enum in (
        AckType,
        ActionType,
        ClimateType,
        DehumidifierMode,
        EquipmentStatus,
        EventType,
        ExtendedHvacMode,
        FanMode,
        HoldType,
        HouseStyle,
        HumidifierMode,
        HvacMode,
        OutputType,
        Owner,
        PlugState,
        RemoteSensorCapabilityType,
        RemoteSensorType,
        ReportJobStatus,
        Scope,
        SelectionType,
        SensorType,
        SensorUsage,
        StateType,
        ThermostatModelNumber,
        VentilatorMode,
    )
}


def _field_name(model, api_field):
    """Resolve an API field name to its constructor argument name."""

    try:
        field_name = model.attribute_name_map[api_field]
    except KeyError:
        return None
    return (
        f"{field_name}_"
        if field_name in keyword.kwlist or hasattr(builtins, field_name)
        else field_name
    )


def _convert(value, type_name, path):
    if value is None:
        return None
    if type_name.startswith("List[") and type_name.endswith("]"):
        if not isinstance(value, list):
            raise EcobeeDeserializationException(f"{path} must be a list")
        item_type = type_name[5:-1]
        return [
            _convert(item, item_type, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if type_name.startswith("Dict[") and type_name.endswith("]"):
        if not isinstance(value, dict):
            raise EcobeeDeserializationException(f"{path} must be an object")
        return value.copy()
    if type_name in {"int", "Long"}:
        if isinstance(value, bool):
            raise EcobeeDeserializationException(f"{path} must be an integer")
        try:
            return int(value)
        except (TypeError, ValueError) as error:
            raise EcobeeDeserializationException(
                f"{path} must be an integer"
            ) from error
    if type_name == "float":
        try:
            return float(value)
        except (TypeError, ValueError) as error:
            raise EcobeeDeserializationException(f"{path} must be a number") from error
    if type_name == "bool":
        if not isinstance(value, bool):
            raise EcobeeDeserializationException(f"{path} must be a boolean")
        return value
    if type_name == "str":
        if isinstance(value, (dict, list)):
            raise EcobeeDeserializationException(f"{path} must be a primitive value")
        return value
    enum = ENUM_REGISTRY.get(type_name)
    if enum:
        try:
            return enum(value)
        except ValueError as error:
            raise EcobeeDeserializationException(
                f"{path} has an invalid {type_name} value"
            ) from error
    model = MODEL_REGISTRY.get(type_name)
    if model is None:
        raise EcobeeDeserializationException(f"{path} has unsupported type {type_name}")
    return deserialize(value, model, path)


def deserialize(data, model, path=None):
    """Construct *model* from an API object without evaluating source text."""
    path = path or model.__name__
    if not isinstance(data, dict):
        raise EcobeeDeserializationException(f"{path} must be an object")

    arguments = {}
    for api_field, value in data.items():
        field_name = _field_name(model, api_field)
        if field_name is None:
            logger.warning("Ignoring unknown field %s on %s", api_field, path)
            continue
        type_name = model.attribute_type_map.get(field_name.rstrip("_"))
        if type_name is None:
            logger.warning(
                "Ignoring field without type metadata %s on %s", api_field, path
            )
            continue
        try:
            arguments[field_name] = _convert(value, type_name, f"{path}.{api_field}")
        except EcobeeDeserializationException as error:
            if "unsupported type" in str(error):
                logger.warning(
                    "Ignoring unsupported object field %s on %s", api_field, path
                )
                continue
            raise

    try:
        return model(**arguments)
    except TypeError as error:
        raise EcobeeDeserializationException(
            f"Unable to construct {path}: {error}"
        ) from error
