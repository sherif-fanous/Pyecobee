from enum import Enum


class AckType(Enum):
    ACCEPT = 'accept'
    DECLINE = 'decline'
    DEFER = 'defer'
    UNACKNOWLEDGED = 'unacknowledged'


class ActionType(Enum):
    ACTIVATE_RELAY = 'activateRelay'
    ADJUST_TEMP = 'adjustTemp'
    DO_NOTHING = 'doNothing'
    SHUTDOWN_AC = 'shutdownAC'
    SHUTDOWN_AUX_HEAT = 'shutdownAuxHeat'
    SHUTDOWN_COMPRESSION = 'shutdownCompression'
    SHUTDOWN_SYSTEM = 'shutdownSystem'
    SWITCH_TO_OCCUPIED = 'switchToOccupied'
    SWITCH_TO_UNOCCUPIED = 'switchToUnoccupied'
    TURN_OFF_DEHUMIDIFER = 'turnOffDehumidifer'
    TURN_OFF_HUMIDIFIER = 'turnOffHumidifier'
    TURN_ON_COOL = 'turnOnCool'
    TURN_ON_DEHUMIDIFIER = 'turnOnDehumidifier'
    TURN_ON_FAN = 'turnOnFan'
    TURN_ON_HEAT = 'turnOnHeat'
    TURN_ON_HUMIDIFIER = 'turnOnHumidifier'


class ClimateType(Enum):
    CALENDAR_EVENT = 'calendarEvent'
    PROGRAM = 'program'


class DehumidifierMode(Enum):
    OFF = 'off'
    ON = 'on'


class EquipmentStatus(Enum):
    AUX_HEAT_1 = 'auxHeat1'
    AUX_HEAT_2 = 'auxHeat2'
    AUX_HEAT_3 = 'auxHeat3'
    AUX_HOT_WATER = 'auxHotWater'
    COMP_COOL_1 = 'compCool1'
    COMP_COOL_2 = 'compCool2'
    COMP_HOT_WATER = 'compHotWater'
    DEHUMIDIFIER = 'dehumidifier'
    ECONOMIZER = 'economizer'
    FAN = 'fan'
    HEAT_PUMP = 'heatPump'
    HEAT_PUMP_2 = 'heatPump2'
    HEAT_PUMP_3 = 'heatPump3'
    HUMIDIFIER = 'humidifier'
    VENTILATOR = 'ventilator'


class EventType(Enum):
    AUTO_AWAY = 'autoAway'
    AUTO_HOME = 'autoHome'
    DEMAND_RESPONSE = 'demandResponse'
    HOLD = 'hold'
    QUICK_SAVE = 'quickSave'
    SENSOR = 'sensor'
    SWITCH_OCCUPANCY = 'switchOccupancy'
    TODAY = 'today'
    VACATION = 'vacation'


class ExtendedHvacMode(Enum):
    COMPRESSOR_COOL_OFF = 'compressorCoolOff'
    COMPRESSOR_COOL_STAGE_10N = 'compressorCoolStage10n'
    COMPRESSOR_COOL_STAGE_20N = 'compressorCoolStage20n'
    COMPRESSOR_HEAT_OFF = 'compressorHeatOff'
    COMPRESSOR_HEAT_STAGE_10N = 'compressorHeatStage10n'
    COMPRESSOR_HEAT_STAGE_20N = 'compressorHeatStage20n'
    ECONOMY_CYCLE = 'economyCycle'
    HEAT_OFF = 'heatOff'
    HEAT_STAGE_10N = 'heatStage10n'
    HEAT_STAGE_20N = 'heatStage20n'
    HEAT_STAGE_30N = 'heatStage30n'


class FanMode(Enum):
    AUTO = 'auto'
    ON = 'on'


class HoldType(Enum):
    HOLD_HOURS = 'holdHours'
    INDEFINITE = 'indefinite'
    NEXT_TRANSITION = 'nextTransition'
    DATE_TIME = 'dateTime'


class HouseStyle(Enum):
    APARTMENT = 'apartment'
    CONDOMINIUM = 'condominium'
    DETACHED = 'detached'
    LOFT = 'loft'
    MULTI_PLEX = 'multiPlex'
    OTHER = 'other'
    ROW_HOUSE = 'rowHouse'
    SEMI_DETACHED = 'semiDetached'
    TOWNHOUSE = 'townhouse'
    UNKNOWN = '0'


class HumidifierMode(Enum):
    AUTO = 'auto'
    MANUAL = 'manual'
    OFF = 'off'


class HvacMode(Enum):
    AUTO = 'auto'
    AUX_HEAT_ONLY = 'auxHeatOnly'
    COOL = 'cool'
    HEAT = 'heat'
    OFF = 'off'


class OutputType(Enum):
    COMPRESSOR_1 = 'compressor1'
    COMPRESSOR_2 = 'compressor2'
    DEHUMIDIFIER = 'dehumidifier'
    ECONOMIZER = 'economizer'
    FAN = 'fan'
    HEAT_1 = 'heat1'
    HEAT_2 = 'heat2'
    HEAT_3 = 'heat3'
    HEAT_PUMP_REVERSAL = 'heatPumpReversal'
    HUMIDIFIER = 'humidifier'
    NONE = 'none'
    OCCUPANCY = 'occupancy'
    USER_DEFINED = 'userDefined'
    VENTILATOR = 'ventilator'
    ZONE_COOL = 'zoneCool'
    ZONE_FAN = 'zoneFan'
    ZONE_HEAT = 'zoneHeat'


class Owner(Enum):
    AD_HOC = 'adHoc'
    DEMAND_RESPONSE = 'demandResponse'
    QUICK_SAVE = 'quickSave'
    SENSOR_ACTION = 'sensorAction'
    SWITCH_OCCUPANCY = 'switchOccupancy'
    SYSTEM = 'system'
    TEMPLATE = 'template'
    USER = 'user'


class PlugState(Enum):
    OFF = 'off'
    ON = 'on'
    RESUME = 'resume'


class RemoteSensorCapabilityType(Enum):
    ADC = 'adc'
    CO_2 = 'co2'
    DRY_CONTACT = 'dryContact'
    HUMIDITY = 'humidity'
    OCCUPANCY = 'occupancy'
    TEMPERATURE = 'temperature'
    UNKNOWN = 'unknown'


class RemoteSensorType(Enum):
    CONTROL_SENSOR = 'control_sensor'
    ECOBEE3_REMOTE_SENSOR = 'ecobee3_remote_sensor'
    MONITOR_SENSOR = 'monitor_sensor'
    THERMOSTAT = 'thermostat'


class ReportJobStatus(Enum):
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    ERROR = 'error'
    PROCESSING = 'processing'
    QUEUED = 'queued'


class Scope(Enum):
    EMS = 'ems'
    SMART_READ = 'smartRead'
    SMART_WRITE = 'smartWrite'


class SelectionType(Enum):
    MANAGEMENT_SET = 'managementSet'
    REGISTERED = 'registered'
    THERMOSTATS = 'thermostats'


class SensorType(Enum):
    CO_2 = 'co2'
    CTCLAMP = 'ctclamp'
    DRY_CONTACT = 'dryContact'
    HUMIDITY = 'humidity'
    PLUG = 'plug'
    TEMPERATURE = 'temperature'


class SensorUsage(Enum):
    DISCHARGE_AIR = 'dischargeAir'
    INDOOR = 'indoor'
    MONITOR = 'monitor'
    OUTDOOR = 'outdoor'


class StateType(Enum):
    COOL_HIGH = 'coolHigh'
    COOL_LOW = 'coolLow'
    HEAT_HIGH = 'heatHigh'
    HEAT_LOW = 'heatLow'
    HIGH = 'high'
    LOW = 'low'
    NORMAL = 'normal'
    TRANSITION_COUNT = 'transitionCount'


class ThermostatModelNumber(Enum):
    ECOBEE_4_SMART = 'apolloSmart'
    ECOBEE_3_EMS = 'athenaEms'
    ECOBEE_3_SMART = 'athenaSmart'
    BRYANT_CARRIER = 'corSmart'
    ECOBEE_SMART_EMS = 'idtEms'
    ECOBEE_SMART = 'idtSmart'
    ECOBEE_3_LITE_EMS = 'nikeEms'
    ECOBEE_3_LITE_SMART = 'nikeSmart'
    ECOBEE_SI_EMS = 'siEms'
    ECOBEE_SI_SMART = 'siSmart'


class VentilatorMode(Enum):
    AUTO = 'auto'
    MIN_ON_TIME = 'minontime'
    ON = 'on'
    OFF = 'off'
