import logging

from pyecobee.ecobee_object import EcobeeObject
from pyecobee.enumerations import AckType
from pyecobee.enumerations import ActionType
from pyecobee.enumerations import ClimateType
from pyecobee.enumerations import DehumidifierMode
from pyecobee.enumerations import EquipmentStatus
from pyecobee.enumerations import EventType
from pyecobee.enumerations import ExtendedHvacMode
from pyecobee.enumerations import FanMode
from pyecobee.enumerations import HoldType
from pyecobee.enumerations import HouseStyle
from pyecobee.enumerations import HumidifierMode
from pyecobee.enumerations import HvacMode
from pyecobee.enumerations import OutputType
from pyecobee.enumerations import Owner
from pyecobee.enumerations import PlugState
from pyecobee.enumerations import RemoteSensorCapabilityType
from pyecobee.enumerations import RemoteSensorType
from pyecobee.enumerations import ReportJobStatus
from pyecobee.enumerations import Scope
from pyecobee.enumerations import SelectionType
from pyecobee.enumerations import SensorType
from pyecobee.enumerations import SensorUsage
from pyecobee.enumerations import StateType
from pyecobee.enumerations import ThermostatModelNumber
from pyecobee.enumerations import VentilatorMode
from pyecobee.exceptions import EcobeeApiException
from pyecobee.exceptions import EcobeeAuthorizationException
from pyecobee.exceptions import EcobeeException
from pyecobee.exceptions import EcobeeHttpException
from pyecobee.exceptions import EcobeeRequestsException
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
from pyecobee.objects.reminder import Reminder
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
from pyecobee.responses import EcobeeAuthorizeResponse
from pyecobee.responses import EcobeeCreateRuntimeReportJobResponse
from pyecobee.responses import EcobeeErrorResponse
from pyecobee.responses import EcobeeGroupsResponse
from pyecobee.responses import EcobeeIssueDemandResponsesResponse
from pyecobee.responses import EcobeeListDemandResponsesResponse
from pyecobee.responses import EcobeeListHierarchySetsResponse
from pyecobee.responses import EcobeeListHierarchyUsersResponse
from pyecobee.responses import EcobeeListRuntimeReportJobStatusResponse
from pyecobee.responses import EcobeeMeterReportsResponse
from pyecobee.responses import EcobeeRuntimeReportsResponse
from pyecobee.responses import EcobeeStatusResponse
from pyecobee.responses import EcobeeThermostatResponse
from pyecobee.responses import EcobeeThermostatsSummaryResponse
from pyecobee.responses import EcobeeTokensResponse
from pyecobee.service import EcobeeService
from pyecobee.utilities import Utilities

try:  # Python 2.X
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
