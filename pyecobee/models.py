"""Pydantic v2 models for ecobee request and response payloads.

Generated from the documented legacy field maps; edit model declarations directly.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from pyecobee.ecobee_object import EcobeeObject, EcobeeResponseObject
from pyecobee.enumerations import FanSpeed, ReportJobStatus, SelectionType


class Action(EcobeeResponseObject):
    type: str
    send_alert: bool | None = Field(None, alias="sendAlert")
    send_update: bool | None = Field(None, alias="sendUpdate")
    activation_delay: int | None = Field(None, alias="activationDelay")
    deactivation_delay: int | None = Field(None, alias="deactivationDelay")
    min_action_duration: int | None = Field(None, alias="minActionDuration")
    heat_adjust_temp: int | None = Field(None, alias="heatAdjustTemp")
    cool_adjust_temp: int | None = Field(None, alias="coolAdjustTemp")
    activate_relay: str | None = Field(None, alias="activateRelay")
    activate_relay_open: bool | None = Field(None, alias="activateRelayOpen")


class Alert(EcobeeResponseObject):
    text: str
    acknowledge_ref: str | None = Field(None, alias="acknowledgeRef")
    date: str | None = None
    time: str | None = None
    severity: str | None = None
    alert_number: int | None = Field(None, alias="alertNumber")
    alert_type: str | None = Field(None, alias="alertType")
    is_operator_alert: bool | None = Field(None, alias="isOperatorAlert")
    reminder: str | None = None
    show_idt: bool | None = Field(None, alias="showIdt")
    show_web: bool | None = Field(None, alias="showWeb")
    send_email: bool | None = Field(None, alias="sendEmail")
    acknowledgement: str | None = None
    remind_me_later: bool | None = Field(None, alias="remindMeLater")
    thermostat_identifier: str | None = Field(None, alias="thermostatIdentifier")
    notification_type: str | None = Field(None, alias="notificationType")


class FanCapabilities(EcobeeResponseObject):
    speed_options: list[FanSpeed] | None = Field(None, alias="speedOptions")


class Capabilities(EcobeeResponseObject):
    fan_capabilities: FanCapabilities | None = Field(None, alias="fanCapabilities")


class Audio(EcobeeResponseObject):
    playback_volume: int | None = Field(None, alias="playbackVolume")
    microphone_enabled: bool | None = Field(None, alias="microphoneEnabled")
    sound_alert_volume: int | None = Field(None, alias="soundAlertVolume")
    sound_tick_volume: int | None = Field(None, alias="soundTickVolume")
    voice_engines: list[VoiceEngine] | None = Field(None, alias="voiceEngines")


class Climate(EcobeeResponseObject):
    name: str
    climate_ref: str | None = Field(None, alias="climateRef")
    is_occupied: bool | None = Field(None, alias="isOccupied")
    is_optimized: bool | None = Field(None, alias="isOptimized")
    cool_fan: str | None = Field(None, alias="coolFan")
    heat_fan: str | None = Field(None, alias="heatFan")
    vent: str | None = None
    ventilator_min_on_time: int | None = Field(None, alias="ventilatorMinOnTime")
    owner: str | None = None
    type: str
    colour: int | None = None
    cool_temp: int | None = Field(None, alias="coolTemp")
    heat_temp: int | None = Field(None, alias="heatTemp")
    sensors: list[RemoteSensor] | None = None


class DemandManagement(EcobeeResponseObject):
    date: str
    hour: int
    temp_offsets: list[int] = Field(..., alias="tempOffsets")


class DemandResponse(EcobeeResponseObject):
    name: str | None = None
    demand_response_ref: str | None = Field(None, alias="demandResponseRef")
    comments: str | None = None
    message: str | None = None
    deferred_date: str | None = Field(None, alias="deferredDate")
    deferred_time: str | None = Field(None, alias="deferredTime")
    show_idt: bool | None = Field(None, alias="showIdt")
    show_web: bool | None = Field(None, alias="showWeb")
    send_email: bool | None = Field(None, alias="sendEmail")
    randomize_start_time: bool | None = Field(None, alias="randomizeStartTime")
    random_start_time_seconds: int | None = Field(None, alias="randomStartTimeSeconds")
    randomize_end_time: bool | None = Field(None, alias="randomizeEndTime")
    random_end_time_seconds: int | None = Field(None, alias="randomEndTimeSeconds")
    event: Event | None = None
    thermostats: list[str] | None = None
    external_ref: str | None = Field(None, alias="externalRef")
    external_ref_type: str | None = Field(None, alias="externalRefType")
    priority: int | None = None


class Device(EcobeeResponseObject):
    device_id: int | None = Field(None, alias="deviceId")
    name: str | None = None
    sensors: list[Sensor] | None = None
    outputs: list[Output] | None = None


class Electricity(EcobeeResponseObject):
    devices: list[ElectricityDevice] | None = None


class ElectricityDevice(EcobeeResponseObject):
    name: str | None = None
    tiers: list[ElectricityTier] | None = None
    last_update: str | None = Field(None, alias="lastUpdate")
    cost: list[str] | None = None
    consumption: list[str] | None = None


class ElectricityTier(EcobeeResponseObject):
    name: str | None = None
    consumption: str | None = None
    cost: str | None = None


class Energy(EcobeeResponseObject):
    tou: TimeOfUse | None = None
    energy_feature_state: str | None = Field(None, alias="energyFeatureState")
    feels_like_mode: str | None = Field(None, alias="feelsLikeMode")
    comfort_preferences: str | None = Field(None, alias="comfortPreferences")


class EquipmentSetting(EcobeeResponseObject):
    type: str
    filter_last_changed: str | None = Field(None, alias="filterLastChanged")
    filter_life: int | None = Field(None, alias="filterLife")
    filter_life_units: str | None = Field(None, alias="filterLifeUnits")
    remind_me_date: str | None = Field(None, alias="remindMeDate")
    enabled: bool | None = None
    remind_technician: bool | None = Field(None, alias="remindTechnician")


class Event(EcobeeResponseObject):
    type: str
    name: str | None = None
    running: bool | None = None
    start_date: str | None = Field(None, alias="startDate")
    start_time: str | None = Field(None, alias="startTime")
    end_date: str | None = Field(None, alias="endDate")
    end_time: str | None = Field(None, alias="endTime")
    is_occupied: bool | None = Field(None, alias="isOccupied")
    is_cool_off: bool | None = Field(None, alias="isCoolOff")
    is_heat_off: bool | None = Field(None, alias="isHeatOff")
    is_indefinite: bool | None = Field(None, alias="isIndefinite")
    cool_hold_temp: int | None = Field(None, alias="coolHoldTemp")
    heat_hold_temp: int | None = Field(None, alias="heatHoldTemp")
    fan: str | None = None
    vent: str | None = None
    ventilator_min_on_time: int | None = Field(None, alias="ventilatorMinOnTime")
    is_optional: bool | None = Field(None, alias="isOptional")
    is_temperature_relative: bool | None = Field(None, alias="isTemperatureRelative")
    cool_relative_temp: int | None = Field(None, alias="coolRelativeTemp")
    heat_relative_temp: int | None = Field(None, alias="heatRelativeTemp")
    is_temperature_absolute: bool | None = Field(None, alias="isTemperatureAbsolute")
    duty_cycle_percentage: int | None = Field(None, alias="dutyCyclePercentage")
    fan_min_on_time: int | None = Field(None, alias="fanMinOnTime")
    occupied_sensor_active: bool | None = Field(None, alias="occupiedSensorActive")
    unoccupied_sensor_active: bool | None = Field(None, alias="unoccupiedSensorActive")
    dr_ramp_up_temp: int | None = Field(None, alias="drRampUpTemp")
    dr_ramp_up_time: int | None = Field(None, alias="drRampUpTime")
    link_ref: str | None = Field(None, alias="linkRef")
    hold_climate_ref: str | None = Field(None, alias="holdClimateRef")
    fan_speed: str | None = Field(None, alias="fanSpeed")


class ExtendedRuntime(EcobeeResponseObject):
    last_reading_timestamp: str | None = Field(None, alias="lastReadingTimestamp")
    runtime_date: str | None = Field(None, alias="runtimeDate")
    runtime_interval: int | None = Field(None, alias="runtimeInterval")
    actual_temperature: list[int] | None = Field(None, alias="actualTemperature")
    actual_humidity: list[int] | None = Field(None, alias="actualHumidity")
    desired_heat: list[int] | None = Field(None, alias="desiredHeat")
    desired_cool: list[int] | None = Field(None, alias="desiredCool")
    desired_humidity: list[int] | None = Field(None, alias="desiredHumidity")
    desired_dehumidity: list[int] | None = Field(None, alias="desiredDehumidity")
    dm_offset: list[int] | None = Field(None, alias="dmOffset")
    hvac_mode: list[str] | None = Field(None, alias="hvacMode")
    heat_pump1: list[int] | None = Field(None, alias="heatPump1")
    heat_pump2: list[int] | None = Field(None, alias="heatPump2")
    aux_heat1: list[int] | None = Field(None, alias="auxHeat1")
    aux_heat2: list[int] | None = Field(None, alias="auxHeat2")
    aux_heat3: list[int] | None = Field(None, alias="auxHeat3")
    cool1: list[int] | None = None
    cool2: list[int] | None = None
    fan: list[int] | None = None
    humidifier: list[int] | None = None
    dehumidifier: list[int] | None = None
    economizer: list[int] | None = None
    ventilator: list[int] | None = None
    current_electricity_bill: int | None = Field(None, alias="currentElectricityBill")
    projected_electricity_bill: int | None = Field(
        None, alias="projectedElectricityBill"
    )


class Function(EcobeeResponseObject):
    type: str
    params: dict[str, object] | None = None


class GeneralSetting(EcobeeResponseObject):
    type: str
    enabled: bool | None = None
    remind_technician: bool | None = Field(None, alias="remindTechnician")


class Group(EcobeeResponseObject):
    group_name: str = Field(..., alias="groupName")
    group_ref: str | None = Field(None, alias="groupRef")
    synchronize_alerts: bool | None = Field(None, alias="synchronizeAlerts")
    synchronize_system_mode: bool | None = Field(None, alias="synchronizeSystemMode")
    synchronize_schedule: bool | None = Field(None, alias="synchronizeSchedule")
    synchronize_quick_save: bool | None = Field(None, alias="synchronizeQuickSave")
    synchronize_reminders: bool | None = Field(None, alias="synchronizeReminders")
    synchronize_contractor_info: bool | None = Field(
        None, alias="synchronizeContractorInfo"
    )
    synchronize_user_preferences: bool | None = Field(
        None, alias="synchronizeUserPreferences"
    )
    synchronize_utility_info: bool | None = Field(None, alias="synchronizeUtilityInfo")
    synchronize_location: bool | None = Field(None, alias="synchronizeLocation")
    synchronize_reset: bool | None = Field(None, alias="synchronizeReset")
    synchronize_vacation: bool | None = Field(None, alias="synchronizeVacation")
    thermostats: list[str] | None = None


class HierarchyPrivilege(EcobeeResponseObject):
    set_path: str = Field(..., alias="setPath")
    user_name: str = Field(..., alias="userName")
    set_name: str | None = Field(None, alias="setName")
    allow_all: bool | None = Field(None, alias="allowAll")
    allow_none: bool | None = Field(None, alias="allowNone")
    allow_view: bool | None = Field(None, alias="allowView")
    allow_program: bool | None = Field(None, alias="allowProgram")
    allow_vacation: bool | None = Field(None, alias="allowVacation")
    allow_settings: bool | None = Field(None, alias="allowSettings")
    allow_details: bool | None = Field(None, alias="allowDetails")
    allow_report: bool | None = Field(None, alias="allowReport")
    allow_security: bool | None = Field(None, alias="allowSecurity")
    allow_hierarchy: bool | None = Field(None, alias="allowHierarchy")
    allow_alerts: bool | None = Field(None, alias="allowAlerts")
    allow_manage_account: bool | None = Field(None, alias="allowManageAccount")


class HierarchySet(EcobeeResponseObject):
    set_name: str = Field(..., alias="setName")
    set_path: str | None = Field(None, alias="setPath")
    children: list[HierarchySet] | None = None
    privileges: list[HierarchyPrivilege] | None = None
    thermostats: list[str] | None = None


class HierarchyUser(EcobeeResponseObject):
    user_name: str = Field(..., alias="userName")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    phone: str | None = None
    last_login: str | None = Field(None, alias="lastLogin")
    active: bool | None = None
    email_alerts: bool | None = Field(None, alias="emailAlerts")


class HouseDetails(EcobeeResponseObject):
    style: str | None = None
    size: int | None = None
    number_of_floors: int | None = Field(None, alias="numberOfFloors")
    number_of_rooms: int | None = Field(None, alias="numberOfRooms")
    number_of_occupants: int | None = Field(None, alias="numberOfOccupants")
    age: int | None = None
    window_efficiency: int | None = Field(None, alias="windowEfficiency")


class LimitSetting(EcobeeResponseObject):
    type: str
    limit: int | None = None
    enabled: bool | None = None
    remind_technician: bool | None = Field(None, alias="remindTechnician")


class Location(EcobeeResponseObject):
    time_zone_offset_minutes: int | None = Field(None, alias="timeZoneOffsetMinutes")
    time_zone: str | None = Field(None, alias="timeZone")
    is_daylight_saving: bool | None = Field(None, alias="isDaylightSaving")
    street_address: str | None = Field(None, alias="streetAddress")
    city: str | None = None
    province_state: str | None = Field(None, alias="provinceState")
    country: str | None = None
    postal_code: str | None = Field(None, alias="postalCode")
    phone_number: str | None = Field(None, alias="phoneNumber")
    map_coordinates: str | None = Field(None, alias="mapCoordinates")


class Management(EcobeeResponseObject):
    administrative_contact: str | None = Field(None, alias="administrativeContact")
    billing_contact: str | None = Field(None, alias="billingContact")
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    web: str | None = None
    show_alert_idt: bool | None = Field(None, alias="showAlertIdt")
    show_alert_web: bool | None = Field(None, alias="showAlertWeb")


class MeterReport(EcobeeResponseObject):
    thermostat_identifier: str | None = Field(None, alias="thermostatIdentifier")
    meter_list: list[MeterReportData] | None = Field(None, alias="meterList")


class MeterReportData(EcobeeResponseObject):
    meter_type: str | None = Field(None, alias="meterType")
    columns: str | None = None
    data: list[str] | None = None


class NotificationSettings(EcobeeResponseObject):
    email_notifications_enabled: bool | None = Field(
        None, alias="emailNotificationsEnabled"
    )
    equipment: list[EquipmentSetting] | None = None
    general: list[GeneralSetting] | None = None
    limit: list[LimitSetting] | None = None


class Output(EcobeeResponseObject):
    name: str | None = None
    zone: int | None = None
    output_id: int | None = Field(None, alias="outputId")
    type: str
    send_update: bool | None = Field(None, alias="sendUpdate")
    active_closed: bool | None = Field(None, alias="activeClosed")
    activation_time: int | None = Field(None, alias="activationTime")
    deactivation_time: int | None = Field(None, alias="deactivationTime")


class Page(EcobeeResponseObject):
    page: int | None = None
    total_pages: int | None = Field(None, alias="totalPages")
    page_size: int | None = Field(None, alias="pageSize")
    total: int | None = None


class Program(EcobeeResponseObject):
    schedule: list[str]
    climates: list[Climate]
    current_climate_ref: str | None = Field(None, alias="currentClimateRef")


class RemoteSensor(EcobeeResponseObject):
    id: str
    name: str | None = None
    type: str
    code: str | None = None
    in_use: bool | None = Field(None, alias="inUse")
    capability: list[RemoteSensorCapability] | None = None


class RemoteSensorCapability(EcobeeResponseObject):
    id: str
    type: str
    value: str | None = None


class ReportJob(EcobeeResponseObject):
    job_id: str | None = Field(None, alias="jobId")
    status: ReportJobStatus | None = None
    message: str | None = None
    files: list[str] | None = None


class Runtime(EcobeeResponseObject):
    runtime_rev: str | None = Field(None, alias="runtimeRev")
    connected: bool | None = None
    equipment_utilization: Any | None = Field(None, alias="equipmentUtilization")
    first_connected: str | None = Field(None, alias="firstConnected")
    connect_date_time: str | None = Field(None, alias="connectDateTime")
    disconnect_date_time: str | None = Field(None, alias="disconnectDateTime")
    last_modified: str | None = Field(None, alias="lastModified")
    last_status_modified: str | None = Field(None, alias="lastStatusModified")
    runtime_date: str | None = Field(None, alias="runtimeDate")
    runtime_interval: int | None = Field(None, alias="runtimeInterval")
    actual_temperature: int | None = Field(None, alias="actualTemperature")
    actual_humidity: int | None = Field(None, alias="actualHumidity")
    raw_temperature: int | None = Field(None, alias="rawTemperature")
    show_icon_mode: int | None = Field(None, alias="showIconMode")
    desired_heat: int | None = Field(None, alias="desiredHeat")
    desired_cool: int | None = Field(None, alias="desiredCool")
    desired_humidity: int | None = Field(None, alias="desiredHumidity")
    desired_dehumidity: int | None = Field(None, alias="desiredDehumidity")
    desired_fan_mode: str | None = Field(None, alias="desiredFanMode")
    desired_heat_range: list[int] | None = Field(None, alias="desiredHeatRange")
    desired_cool_range: list[int] | None = Field(None, alias="desiredCoolRange")


class RuntimeReport(EcobeeResponseObject):
    thermostat_identifier: str | None = Field(None, alias="thermostatIdentifier")
    row_count: int | None = Field(None, alias="rowCount")
    row_list: list[str] | None = Field(None, alias="rowList")


class RuntimeSensorMetadata(EcobeeResponseObject):
    sensor_id: str | None = Field(None, alias="sensorId")
    sensor_name: str | None = Field(None, alias="sensorName")
    sensor_type: str | None = Field(None, alias="sensorType")
    sensor_usage: str | None = Field(None, alias="sensorUsage")


class RuntimeSensorReport(EcobeeResponseObject):
    thermostat_identifier: str | None = Field(None, alias="thermostatIdentifier")
    sensors: list[RuntimeSensorMetadata] | None = None
    columns: list[str] | None = None
    data: list[str] | None = None


class SecuritySettings(EcobeeResponseObject):
    user_access_code: str | None = Field(None, alias="userAccessCode")
    all_user_access: bool | None = Field(None, alias="allUserAccess")
    program_access: bool | None = Field(None, alias="programAccess")
    details_access: bool | None = Field(None, alias="detailsAccess")
    quick_save_access: bool | None = Field(None, alias="quickSaveAccess")
    vacation_access: bool | None = Field(None, alias="vacationAccess")


class Selection(EcobeeObject):
    selection_type: Annotated[SelectionType, Field(alias="selectionType")]
    selection_match: Annotated[str, Field(alias="selectionMatch")]
    include_runtime: Annotated[bool | None, Field(alias="includeRuntime")] = None
    include_extended_runtime: Annotated[
        bool | None, Field(alias="includeExtendedRuntime")
    ] = None
    include_capabilities: Annotated[bool | None, Field(alias="includeCapabilities")] = (
        None
    )
    include_settings: Annotated[bool | None, Field(alias="includeSettings")] = None
    include_location: Annotated[bool | None, Field(alias="includeLocation")] = None
    include_program: Annotated[bool | None, Field(alias="includeProgram")] = None
    include_events: Annotated[bool | None, Field(alias="includeEvents")] = None
    include_device: Annotated[bool | None, Field(alias="includeDevice")] = None
    include_technician: Annotated[bool | None, Field(alias="includeTechnician")] = None
    include_utility: Annotated[bool | None, Field(alias="includeUtility")] = None
    include_management: Annotated[bool | None, Field(alias="includeManagement")] = None
    include_alerts: Annotated[bool | None, Field(alias="includeAlerts")] = None
    include_reminders: Annotated[bool | None, Field(alias="includeReminders")] = None
    include_weather: Annotated[bool | None, Field(alias="includeWeather")] = None
    include_house_details: Annotated[
        bool | None, Field(alias="includeHouseDetails")
    ] = None
    include_oem_cfg: Annotated[bool | None, Field(alias="includeOemCfg")] = None
    include_equipment_status: Annotated[
        bool | None, Field(alias="includeEquipmentStatus")
    ] = None
    include_notification_settings: Annotated[
        bool | None, Field(alias="includeNotificationSettings")
    ] = None
    include_privacy: Annotated[bool | None, Field(alias="includePrivacy")] = None
    include_version: Annotated[bool | None, Field(alias="includeVersion")] = None
    include_security_settings: Annotated[
        bool | None, Field(alias="includeSecuritySettings")
    ] = None
    include_sensors: Annotated[bool | None, Field(alias="includeSensors")] = None
    include_audio: Annotated[bool | None, Field(alias="includeAudio")] = None
    include_energy: Annotated[bool | None, Field(alias="includeEnergy")] = None


class Sensor(EcobeeResponseObject):
    name: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    zone: int | None = None
    sensor_id: int | None = Field(None, alias="sensorId")
    type: str
    usage: str | None = None
    number_of_bits: int | None = Field(None, alias="numberOfBits")
    bconstant: int | None = None
    thermistor_size: int | None = Field(None, alias="thermistorSize")
    temp_correction: int | None = Field(None, alias="tempCorrection")
    gain: int | None = None
    max_voltage: int | None = Field(None, alias="maxVoltage")
    multiplier: int | None = None
    states: list[State] | None = None


class Settings(EcobeeResponseObject):
    display_air_quality: bool | None = Field(None, alias="displayAirQuality")
    hvac_mode: str | None = Field(None, alias="hvacMode")
    last_service_date: str | None = Field(None, alias="lastServiceDate")
    service_remind_me: bool | None = Field(None, alias="serviceRemindMe")
    months_between_service: int | None = Field(None, alias="monthsBetweenService")
    remind_me_date: str | None = Field(None, alias="remindMeDate")
    vent: str | None = None
    ventilator_min_on_time: int | None = Field(None, alias="ventilatorMinOnTime")
    service_remind_technician: bool | None = Field(
        None, alias="serviceRemindTechnician"
    )
    ei_location: str | None = Field(None, alias="eiLocation")
    cold_temp_alert: int | None = Field(None, alias="coldTempAlert")
    cold_temp_alert_enabled: bool | None = Field(None, alias="coldTempAlertEnabled")
    hot_temp_alert: int | None = Field(None, alias="hotTempAlert")
    hot_temp_alert_enabled: bool | None = Field(None, alias="hotTempAlertEnabled")
    cool_stages: int | None = Field(None, alias="coolStages")
    heat_stages: int | None = Field(None, alias="heatStages")
    max_set_back: int | None = Field(None, alias="maxSetBack")
    max_set_forward: int | None = Field(None, alias="maxSetForward")
    quick_save_set_back: int | None = Field(None, alias="quickSaveSetBack")
    quick_save_set_forward: int | None = Field(None, alias="quickSaveSetForward")
    has_heat_pump: bool | None = Field(None, alias="hasHeatPump")
    has_forced_air: bool | None = Field(None, alias="hasForcedAir")
    has_boiler: bool | None = Field(None, alias="hasBoiler")
    has_humidifier: bool | None = Field(None, alias="hasHumidifier")
    has_erv: bool | None = Field(None, alias="hasErv")
    has_hrv: bool | None = Field(None, alias="hasHrv")
    condensation_avoid: bool | None = Field(None, alias="condensationAvoid")
    use_celsius: bool | None = Field(None, alias="useCelsius")
    use_time_format12: bool | None = Field(None, alias="useTimeFormat12")
    locale: str | None = None
    humidity: str | None = None
    humidifier_mode: str | None = Field(None, alias="humidifierMode")
    backlight_on_intensity: int | None = Field(None, alias="backlightOnIntensity")
    backlight_sleep_intensity: int | None = Field(None, alias="backlightSleepIntensity")
    backlight_off_time: int | None = Field(None, alias="backlightOffTime")
    sound_tick_volume: int | None = Field(None, alias="soundTickVolume")
    sound_alert_volume: int | None = Field(None, alias="soundAlertVolume")
    compressor_protection_min_time: int | None = Field(
        None, alias="compressorProtectionMinTime"
    )
    compressor_protection_min_temp: int | None = Field(
        None, alias="compressorProtectionMinTemp"
    )
    stage1_heating_differential_temp: int | None = Field(
        None, alias="stage1HeatingDifferentialTemp"
    )
    stage1_cooling_differential_temp: int | None = Field(
        None, alias="stage1CoolingDifferentialTemp"
    )
    stage1_heating_dissipation_time: int | None = Field(
        None, alias="stage1HeatingDissipationTime"
    )
    stage1_cooling_dissipation_time: int | None = Field(
        None, alias="stage1CoolingDissipationTime"
    )
    heat_pump_reversal_on_cool: bool | None = Field(
        None, alias="heatPumpReversalOnCool"
    )
    fan_control_required: bool | None = Field(None, alias="fanControlRequired")
    fan_min_on_time: int | None = Field(None, alias="fanMinOnTime")
    heat_cool_min_delta: int | None = Field(None, alias="heatCoolMinDelta")
    temp_correction: int | None = Field(None, alias="tempCorrection")
    hold_action: str | None = Field(None, alias="holdAction")
    heat_pump_ground_water: bool | None = Field(None, alias="heatPumpGroundWater")
    has_electric: bool | None = Field(None, alias="hasElectric")
    has_dehumidifier: bool | None = Field(None, alias="hasDehumidifier")
    dehumidifier_mode: str | None = Field(None, alias="dehumidifierMode")
    dehumidifier_level: int | None = Field(None, alias="dehumidifierLevel")
    dehumidify_with_a_c: bool | None = Field(None, alias="dehumidifyWithAC")
    dehumidify_overcool_offset: int | None = Field(
        None, alias="dehumidifyOvercoolOffset"
    )
    auto_heat_cool_feature_enabled: bool | None = Field(
        None, alias="autoHeatCoolFeatureEnabled"
    )
    wifi_offline_alert: bool | None = Field(None, alias="wifiOfflineAlert")
    heat_min_temp: int | None = Field(None, alias="heatMinTemp")
    heat_max_temp: int | None = Field(None, alias="heatMaxTemp")
    cool_min_temp: int | None = Field(None, alias="coolMinTemp")
    cool_max_temp: int | None = Field(None, alias="coolMaxTemp")
    heat_range_high: int | None = Field(None, alias="heatRangeHigh")
    heat_range_low: int | None = Field(None, alias="heatRangeLow")
    cool_range_high: int | None = Field(None, alias="coolRangeHigh")
    cool_range_low: int | None = Field(None, alias="coolRangeLow")
    user_access_code: str | None = Field(None, alias="userAccessCode")
    user_access_setting: int | None = Field(None, alias="userAccessSetting")
    aux_runtime_alert: int | None = Field(None, alias="auxRuntimeAlert")
    aux_outdoor_temp_alert: int | None = Field(None, alias="auxOutdoorTempAlert")
    aux_max_outdoor_temp: int | None = Field(None, alias="auxMaxOutdoorTemp")
    aux_runtime_alert_notify: bool | None = Field(None, alias="auxRuntimeAlertNotify")
    aux_outdoor_temp_alert_notify: bool | None = Field(
        None, alias="auxOutdoorTempAlertNotify"
    )
    aux_runtime_alert_notify_technician: bool | None = Field(
        None, alias="auxRuntimeAlertNotifyTechnician"
    )
    aux_outdoor_temp_alert_notify_technician: bool | None = Field(
        None, alias="auxOutdoorTempAlertNotifyTechnician"
    )
    disable_pre_heating: bool | None = Field(None, alias="disablePreHeating")
    disable_pre_cooling: bool | None = Field(None, alias="disablePreCooling")
    installer_code_required: bool | None = Field(None, alias="installerCodeRequired")
    dr_accept: str | None = Field(None, alias="drAccept")
    is_rental_property: bool | None = Field(None, alias="isRentalProperty")
    use_zone_controller: bool | None = Field(None, alias="useZoneController")
    random_start_delay_cool: int | None = Field(None, alias="randomStartDelayCool")
    random_start_delay_heat: int | None = Field(None, alias="randomStartDelayHeat")
    humidity_high_alert: int | None = Field(None, alias="humidityHighAlert")
    humidity_low_alert: int | None = Field(None, alias="humidityLowAlert")
    disable_heat_pump_alerts: bool | None = Field(None, alias="disableHeatPumpAlerts")
    disable_alerts_on_idt: bool | None = Field(None, alias="disableAlertsOnIdt")
    humidity_alert_notify: bool | None = Field(None, alias="humidityAlertNotify")
    humidity_alert_notify_technician: bool | None = Field(
        None, alias="humidityAlertNotifyTechnician"
    )
    temp_alert_notify: bool | None = Field(None, alias="tempAlertNotify")
    temp_alert_notify_technician: bool | None = Field(
        None, alias="tempAlertNotifyTechnician"
    )
    monthly_electricity_bill_limit: int | None = Field(
        None, alias="monthlyElectricityBillLimit"
    )
    enable_electricity_bill_alert: bool | None = Field(
        None, alias="enableElectricityBillAlert"
    )
    enable_projected_electricity_bill_alert: bool | None = Field(
        None, alias="enableProjectedElectricityBillAlert"
    )
    electricity_billing_day_of_month: int | None = Field(
        None, alias="electricityBillingDayOfMonth"
    )
    electricity_bill_cycle_months: int | None = Field(
        None, alias="electricityBillCycleMonths"
    )
    electricity_bill_start_month: int | None = Field(
        None, alias="electricityBillStartMonth"
    )
    ventilator_min_on_time_home: int | None = Field(
        None, alias="ventilatorMinOnTimeHome"
    )
    ventilator_min_on_time_away: int | None = Field(
        None, alias="ventilatorMinOnTimeAway"
    )
    backlight_off_during_sleep: bool | None = Field(
        None, alias="backlightOffDuringSleep"
    )
    auto_away: bool | None = Field(None, alias="autoAway")
    smart_circulation: bool | None = Field(None, alias="smartCirculation")
    follow_me_comfort: bool | None = Field(None, alias="followMeComfort")
    ventilator_type: str | None = Field(None, alias="ventilatorType")
    is_ventilator_timer_on: bool | None = Field(None, alias="isVentilatorTimerOn")
    ventilator_off_date_time: str | None = Field(None, alias="ventilatorOffDateTime")
    has_u_v_filter: bool | None = Field(None, alias="hasUVFilter")
    cooling_lockout: bool | None = Field(None, alias="coolingLockout")
    ventilator_free_cooling: bool | None = Field(None, alias="ventilatorFreeCooling")
    dehumidify_when_heating: bool | None = Field(None, alias="dehumidifyWhenHeating")
    ventilator_dehumidify: bool | None = Field(None, alias="ventilatorDehumidify")
    group_ref: str | None = Field(None, alias="groupRef")
    group_name: str | None = Field(None, alias="groupName")
    group_setting: int | None = Field(None, alias="groupSetting")
    fan_speed: str | None = Field(None, alias="fanSpeed")


class State(EcobeeResponseObject):
    max_value: int | None = Field(None, alias="maxValue")
    min_value: int | None = Field(None, alias="minValue")
    type: str
    actions: list[Action] | None = None


class Status(EcobeeResponseObject):
    code: int | None = None
    message: str | None = None


class Technician(EcobeeResponseObject):
    contractor_ref: str | None = Field(None, alias="contractorRef")
    name: str | None = None
    phone: str | None = None
    street_address: str | None = Field(None, alias="streetAddress")
    city: str | None = None
    province_state: str | None = Field(None, alias="provinceState")
    country: str | None = None
    postal_code: str | None = Field(None, alias="postalCode")
    email: str | None = None
    web: str | None = None


class Thermostat(EcobeeResponseObject):
    identifier: str
    name: str | None = None
    thermostat_rev: str | None = Field(None, alias="thermostatRev")
    is_registered: bool | None = Field(None, alias="isRegistered")
    model_number: str | None = Field(None, alias="modelNumber")
    brand: str | None = None
    features: str | None = None
    last_modified: str | None = Field(None, alias="lastModified")
    thermostat_time: str | None = Field(None, alias="thermostatTime")
    utc_time: str | None = Field(None, alias="utcTime")
    audio: Audio | None = None
    capabilities: Capabilities | None = None
    alerts: list[Alert] | None = None
    reminders: list[Any] | None = None
    settings: Settings | None = None
    runtime: Runtime | None = None
    extended_runtime: ExtendedRuntime | None = Field(None, alias="extendedRuntime")
    devices: list[Device] | None = None
    location: Location | None = None
    technician: Technician | None = None
    utility: Utility | None = None
    management: Management | None = None
    weather: Weather | None = None
    events: list[Event] | None = None
    program: Program | None = None
    house_details: HouseDetails | None = Field(None, alias="houseDetails")
    oem_cfg: Any | None = Field(None, alias="oemCfg")
    equipment_status: str | None = Field(None, alias="equipmentStatus")
    notification_settings: NotificationSettings | None = Field(
        None, alias="notificationSettings"
    )
    privacy: Any | None = None
    version: Version | None = None
    security_settings: SecuritySettings | None = Field(None, alias="securitySettings")
    filter_subscription: Any | None = Field(None, alias="filterSubscription")
    remote_sensors: list[RemoteSensor] | None = Field(None, alias="remoteSensors")


class TimeOfUse(EcobeeResponseObject):
    feature_state: str | None = Field(None, alias="featureState")
    savings: str | None = None


class User(EcobeeResponseObject):
    user_name: str = Field(..., alias="userName")
    display_name: str | None = Field(None, alias="displayName")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    honorific: str | None = None
    register_date: str | None = Field(None, alias="registerDate")
    register_time: str | None = Field(None, alias="registerTime")
    default_thermostat_identifier: str | None = Field(
        None, alias="defaultThermostatIdentifier"
    )
    management_ref: str | None = Field(None, alias="managementRef")
    utility_ref: str | None = Field(None, alias="utilityRef")
    support_ref: str | None = Field(None, alias="supportRef")
    phone_number: str | None = Field(None, alias="phoneNumber")
    utility_time_zone: str | None = Field(None, alias="utilityTimeZone")
    management_time_zone: str | None = Field(None, alias="managementTimeZone")
    is_residential: bool | None = Field(None, alias="isResidential")
    is_developer: bool | None = Field(None, alias="isDeveloper")
    is_management: bool | None = Field(None, alias="isManagement")
    is_utility: bool | None = Field(None, alias="isUtility")
    is_contractor: bool | None = Field(None, alias="isContractor")


class Utility(EcobeeResponseObject):
    id: str | None = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    web: str | None = None


class Version(EcobeeResponseObject):
    thermostat_firmware_version: str | None = Field(
        None, alias="thermostatFirmwareVersion"
    )


class VoiceEngine(EcobeeResponseObject):
    name: str | None = None
    enabled: bool | None = None


class Weather(EcobeeResponseObject):
    timestamp: str | None = None
    weather_station: str | None = Field(None, alias="weatherStation")
    forecasts: list[WeatherForecast] | None = None


class WeatherForecast(EcobeeResponseObject):
    weather_symbol: int | None = Field(None, alias="weatherSymbol")
    date_time: str | None = Field(None, alias="dateTime")
    condition: str | None = None
    temperature: int | None = None
    pressure: int | None = None
    relative_humidity: int | None = Field(None, alias="relativeHumidity")
    dewpoint: int | None = None
    visibility: int | None = None
    wind_speed: int | None = Field(None, alias="windSpeed")
    wind_gust: int | None = Field(None, alias="windGust")
    wind_direction: str | None = Field(None, alias="windDirection")
    wind_bearing: int | None = Field(None, alias="windBearing")
    pop: int | None = None
    temp_high: int | None = Field(None, alias="tempHigh")
    temp_low: int | None = Field(None, alias="tempLow")
    sky: int | None = None


class EcobeeStatusResponse(EcobeeResponseObject):
    status: Status


class EcobeeAuthorizeResponse(EcobeeResponseObject):
    ecobee_pin: str = Field(..., alias="ecobeePin")
    code: str
    scope: str
    expires_in: int
    interval: int


class EcobeeCreateRuntimeReportJobResponse(EcobeeStatusResponse):
    job_id: str = Field(..., alias="jobId")
    job_status: ReportJobStatus = Field(..., alias="jobStatus")
    status: Status


class EcobeeErrorResponse(EcobeeResponseObject):
    error: str
    error_description: str
    error_uri: str


class EcobeeGroupsResponse(EcobeeStatusResponse):
    groups: list[Group]
    status: Status


class EcobeeIssueDemandResponsesResponse(EcobeeStatusResponse):
    demand_response_ref: str = Field(..., alias="demandResponseRef")
    status: Status


class EcobeeListDemandResponsesResponse(EcobeeStatusResponse):
    demand_response_list: list[DemandResponse] = Field(..., alias="drList")
    status: Status


class EcobeeListHierarchySetsResponse(EcobeeStatusResponse):
    sets: list[HierarchySet]
    status: Status


class EcobeeListHierarchyUsersResponse(EcobeeStatusResponse):
    users: list[HierarchyUser]
    privileges: list[HierarchyPrivilege] | None = None
    status: Status


class EcobeeListRuntimeReportJobStatusResponse(EcobeeStatusResponse):
    jobs: list[ReportJob]
    status: Status


class EcobeeMeterReportsResponse(EcobeeStatusResponse):
    report_list: list[MeterReport] = Field(..., alias="reportList")
    status: Status


class EcobeeRuntimeReportsResponse(EcobeeStatusResponse):
    start_date: str = Field(..., alias="startDate")
    start_interval: int = Field(..., alias="startInterval")
    end_date: str = Field(..., alias="endDate")
    end_interval: int = Field(..., alias="endInterval")
    columns: str
    report_list: list[RuntimeReport] = Field(..., alias="reportList")
    sensor_list: list[RuntimeSensorReport] = Field(..., alias="sensorList")
    status: Status


class EcobeeThermostatResponse(EcobeeStatusResponse):
    page: Page
    thermostat_list: list[Thermostat] = Field(..., alias="thermostatList")
    status: Status


class EcobeeThermostatsSummaryResponse(EcobeeStatusResponse):
    revision_list: list[str] = Field(..., alias="revisionList")
    thermostat_count: int = Field(..., alias="thermostatCount")
    status_list: list[str] = Field(..., alias="statusList")
    status: Status


class EcobeeTokensResponse(EcobeeResponseObject):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


ALL_MODELS = tuple(
    value
    for value in globals().values()
    if isinstance(value, type)
    and issubclass(value, EcobeeObject)
    and value not in {EcobeeObject, EcobeeResponseObject}
)

for model in ALL_MODELS:
    model.model_rebuild()
