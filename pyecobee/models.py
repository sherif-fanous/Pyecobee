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
    send_alert: Annotated[bool | None, Field(alias="sendAlert")] = None
    send_update: Annotated[bool | None, Field(alias="sendUpdate")] = None
    activation_delay: Annotated[int | None, Field(alias="activationDelay")] = None
    deactivation_delay: Annotated[int | None, Field(alias="deactivationDelay")] = None
    min_action_duration: Annotated[int | None, Field(alias="minActionDuration")] = None
    heat_adjust_temp: Annotated[int | None, Field(alias="heatAdjustTemp")] = None
    cool_adjust_temp: Annotated[int | None, Field(alias="coolAdjustTemp")] = None
    activate_relay: Annotated[str | None, Field(alias="activateRelay")] = None
    activate_relay_open: Annotated[bool | None, Field(alias="activateRelayOpen")] = None


class Alert(EcobeeResponseObject):
    text: str
    acknowledge_ref: Annotated[str | None, Field(alias="acknowledgeRef")] = None
    date: str | None = None
    time: str | None = None
    severity: str | None = None
    alert_number: Annotated[int | None, Field(alias="alertNumber")] = None
    alert_type: Annotated[str | None, Field(alias="alertType")] = None
    is_operator_alert: Annotated[bool | None, Field(alias="isOperatorAlert")] = None
    reminder: str | None = None
    show_idt: Annotated[bool | None, Field(alias="showIdt")] = None
    show_web: Annotated[bool | None, Field(alias="showWeb")] = None
    send_email: Annotated[bool | None, Field(alias="sendEmail")] = None
    acknowledgement: str | None = None
    remind_me_later: Annotated[bool | None, Field(alias="remindMeLater")] = None
    thermostat_identifier: Annotated[
        str | None, Field(alias="thermostatIdentifier")
    ] = None
    notification_type: Annotated[str | None, Field(alias="notificationType")] = None


class FanCapabilities(EcobeeResponseObject):
    speed_options: Annotated[list[FanSpeed] | None, Field(alias="speedOptions")] = None


class Capabilities(EcobeeResponseObject):
    fan_capabilities: Annotated[
        FanCapabilities | None, Field(alias="fanCapabilities")
    ] = None


class Audio(EcobeeResponseObject):
    playback_volume: Annotated[int | None, Field(alias="playbackVolume")] = None
    microphone_enabled: Annotated[bool | None, Field(alias="microphoneEnabled")] = None
    sound_alert_volume: Annotated[int | None, Field(alias="soundAlertVolume")] = None
    sound_tick_volume: Annotated[int | None, Field(alias="soundTickVolume")] = None
    voice_engines: Annotated[list[VoiceEngine] | None, Field(alias="voiceEngines")] = (
        None
    )


class Climate(EcobeeResponseObject):
    name: str
    climate_ref: Annotated[str | None, Field(alias="climateRef")] = None
    is_occupied: Annotated[bool | None, Field(alias="isOccupied")] = None
    is_optimized: Annotated[bool | None, Field(alias="isOptimized")] = None
    cool_fan: Annotated[str | None, Field(alias="coolFan")] = None
    heat_fan: Annotated[str | None, Field(alias="heatFan")] = None
    vent: str | None = None
    ventilator_min_on_time: Annotated[
        int | None, Field(alias="ventilatorMinOnTime")
    ] = None
    owner: str | None = None
    type: str
    colour: int | None = None
    cool_temp: Annotated[int | None, Field(alias="coolTemp")] = None
    heat_temp: Annotated[int | None, Field(alias="heatTemp")] = None
    sensors: list[RemoteSensor] | None = None


class DemandManagement(EcobeeResponseObject):
    date: str
    hour: int
    temp_offsets: Annotated[list[int], Field(alias="tempOffsets")]


class DemandResponse(EcobeeResponseObject):
    name: str | None = None
    demand_response_ref: Annotated[str | None, Field(alias="demandResponseRef")] = None
    comments: str | None = None
    message: str | None = None
    deferred_date: Annotated[str | None, Field(alias="deferredDate")] = None
    deferred_time: Annotated[str | None, Field(alias="deferredTime")] = None
    show_idt: Annotated[bool | None, Field(alias="showIdt")] = None
    show_web: Annotated[bool | None, Field(alias="showWeb")] = None
    send_email: Annotated[bool | None, Field(alias="sendEmail")] = None
    randomize_start_time: Annotated[bool | None, Field(alias="randomizeStartTime")] = (
        None
    )
    random_start_time_seconds: Annotated[
        int | None, Field(alias="randomStartTimeSeconds")
    ] = None
    randomize_end_time: Annotated[bool | None, Field(alias="randomizeEndTime")] = None
    random_end_time_seconds: Annotated[
        int | None, Field(alias="randomEndTimeSeconds")
    ] = None
    event: Event | None = None
    thermostats: list[str] | None = None
    external_ref: Annotated[str | None, Field(alias="externalRef")] = None
    external_ref_type: Annotated[str | None, Field(alias="externalRefType")] = None
    priority: int | None = None


class Device(EcobeeResponseObject):
    device_id: Annotated[int | None, Field(alias="deviceId")] = None
    name: str | None = None
    sensors: list[Sensor] | None = None
    outputs: list[Output] | None = None


class Electricity(EcobeeResponseObject):
    devices: list[ElectricityDevice] | None = None


class ElectricityDevice(EcobeeResponseObject):
    name: str | None = None
    tiers: list[ElectricityTier] | None = None
    last_update: Annotated[str | None, Field(alias="lastUpdate")] = None
    cost: list[str] | None = None
    consumption: list[str] | None = None


class ElectricityTier(EcobeeResponseObject):
    name: str | None = None
    consumption: str | None = None
    cost: str | None = None


class Energy(EcobeeResponseObject):
    tou: TimeOfUse | None = None
    energy_feature_state: Annotated[str | None, Field(alias="energyFeatureState")] = (
        None
    )
    feels_like_mode: Annotated[str | None, Field(alias="feelsLikeMode")] = None
    comfort_preferences: Annotated[str | None, Field(alias="comfortPreferences")] = None


class EquipmentSetting(EcobeeResponseObject):
    type: str
    filter_last_changed: Annotated[str | None, Field(alias="filterLastChanged")] = None
    filter_life: Annotated[int | None, Field(alias="filterLife")] = None
    filter_life_units: Annotated[str | None, Field(alias="filterLifeUnits")] = None
    remind_me_date: Annotated[str | None, Field(alias="remindMeDate")] = None
    enabled: bool | None = None
    remind_technician: Annotated[bool | None, Field(alias="remindTechnician")] = None


class Event(EcobeeResponseObject):
    type: str
    name: str | None = None
    running: bool | None = None
    start_date: Annotated[str | None, Field(alias="startDate")] = None
    start_time: Annotated[str | None, Field(alias="startTime")] = None
    end_date: Annotated[str | None, Field(alias="endDate")] = None
    end_time: Annotated[str | None, Field(alias="endTime")] = None
    is_occupied: Annotated[bool | None, Field(alias="isOccupied")] = None
    is_cool_off: Annotated[bool | None, Field(alias="isCoolOff")] = None
    is_heat_off: Annotated[bool | None, Field(alias="isHeatOff")] = None
    is_indefinite: Annotated[bool | None, Field(alias="isIndefinite")] = None
    cool_hold_temp: Annotated[int | None, Field(alias="coolHoldTemp")] = None
    heat_hold_temp: Annotated[int | None, Field(alias="heatHoldTemp")] = None
    fan: str | None = None
    vent: str | None = None
    ventilator_min_on_time: Annotated[
        int | None, Field(alias="ventilatorMinOnTime")
    ] = None
    is_optional: Annotated[bool | None, Field(alias="isOptional")] = None
    is_temperature_relative: Annotated[
        bool | None, Field(alias="isTemperatureRelative")
    ] = None
    cool_relative_temp: Annotated[int | None, Field(alias="coolRelativeTemp")] = None
    heat_relative_temp: Annotated[int | None, Field(alias="heatRelativeTemp")] = None
    is_temperature_absolute: Annotated[
        bool | None, Field(alias="isTemperatureAbsolute")
    ] = None
    duty_cycle_percentage: Annotated[int | None, Field(alias="dutyCyclePercentage")] = (
        None
    )
    fan_min_on_time: Annotated[int | None, Field(alias="fanMinOnTime")] = None
    occupied_sensor_active: Annotated[
        bool | None, Field(alias="occupiedSensorActive")
    ] = None
    unoccupied_sensor_active: Annotated[
        bool | None, Field(alias="unoccupiedSensorActive")
    ] = None
    dr_ramp_up_temp: Annotated[int | None, Field(alias="drRampUpTemp")] = None
    dr_ramp_up_time: Annotated[int | None, Field(alias="drRampUpTime")] = None
    link_ref: Annotated[str | None, Field(alias="linkRef")] = None
    hold_climate_ref: Annotated[str | None, Field(alias="holdClimateRef")] = None
    fan_speed: Annotated[str | None, Field(alias="fanSpeed")] = None


class ExtendedRuntime(EcobeeResponseObject):
    last_reading_timestamp: Annotated[
        str | None, Field(alias="lastReadingTimestamp")
    ] = None
    runtime_date: Annotated[str | None, Field(alias="runtimeDate")] = None
    runtime_interval: Annotated[int | None, Field(alias="runtimeInterval")] = None
    actual_temperature: Annotated[
        list[int] | None, Field(alias="actualTemperature")
    ] = None
    actual_humidity: Annotated[list[int] | None, Field(alias="actualHumidity")] = None
    desired_heat: Annotated[list[int] | None, Field(alias="desiredHeat")] = None
    desired_cool: Annotated[list[int] | None, Field(alias="desiredCool")] = None
    desired_humidity: Annotated[list[int] | None, Field(alias="desiredHumidity")] = None
    desired_dehumidity: Annotated[
        list[int] | None, Field(alias="desiredDehumidity")
    ] = None
    dm_offset: Annotated[list[int] | None, Field(alias="dmOffset")] = None
    hvac_mode: Annotated[list[str] | None, Field(alias="hvacMode")] = None
    heat_pump1: Annotated[list[int] | None, Field(alias="heatPump1")] = None
    heat_pump2: Annotated[list[int] | None, Field(alias="heatPump2")] = None
    aux_heat1: Annotated[list[int] | None, Field(alias="auxHeat1")] = None
    aux_heat2: Annotated[list[int] | None, Field(alias="auxHeat2")] = None
    aux_heat3: Annotated[list[int] | None, Field(alias="auxHeat3")] = None
    cool1: list[int] | None = None
    cool2: list[int] | None = None
    fan: list[int] | None = None
    humidifier: list[int] | None = None
    dehumidifier: list[int] | None = None
    economizer: list[int] | None = None
    ventilator: list[int] | None = None
    current_electricity_bill: Annotated[
        int | None, Field(alias="currentElectricityBill")
    ] = None
    projected_electricity_bill: Annotated[
        int | None, Field(alias="projectedElectricityBill")
    ] = None


class Function(EcobeeResponseObject):
    type: str
    params: dict[str, object] | None = None


class GeneralSetting(EcobeeResponseObject):
    type: str
    enabled: bool | None = None
    remind_technician: Annotated[bool | None, Field(alias="remindTechnician")] = None


class Group(EcobeeResponseObject):
    group_name: Annotated[str, Field(alias="groupName")]
    group_ref: Annotated[str | None, Field(alias="groupRef")] = None
    synchronize_alerts: Annotated[bool | None, Field(alias="synchronizeAlerts")] = None
    synchronize_system_mode: Annotated[
        bool | None, Field(alias="synchronizeSystemMode")
    ] = None
    synchronize_schedule: Annotated[bool | None, Field(alias="synchronizeSchedule")] = (
        None
    )
    synchronize_quick_save: Annotated[
        bool | None, Field(alias="synchronizeQuickSave")
    ] = None
    synchronize_reminders: Annotated[
        bool | None, Field(alias="synchronizeReminders")
    ] = None
    synchronize_contractor_info: Annotated[
        bool | None, Field(alias="synchronizeContractorInfo")
    ] = None
    synchronize_user_preferences: Annotated[
        bool | None, Field(alias="synchronizeUserPreferences")
    ] = None
    synchronize_utility_info: Annotated[
        bool | None, Field(alias="synchronizeUtilityInfo")
    ] = None
    synchronize_location: Annotated[bool | None, Field(alias="synchronizeLocation")] = (
        None
    )
    synchronize_reset: Annotated[bool | None, Field(alias="synchronizeReset")] = None
    synchronize_vacation: Annotated[bool | None, Field(alias="synchronizeVacation")] = (
        None
    )
    thermostats: list[str] | None = None


class HierarchyPrivilege(EcobeeResponseObject):
    set_path: Annotated[str, Field(alias="setPath")]
    user_name: Annotated[str, Field(alias="userName")]
    set_name: Annotated[str | None, Field(alias="setName")] = None
    allow_all: Annotated[bool | None, Field(alias="allowAll")] = None
    allow_none: Annotated[bool | None, Field(alias="allowNone")] = None
    allow_view: Annotated[bool | None, Field(alias="allowView")] = None
    allow_program: Annotated[bool | None, Field(alias="allowProgram")] = None
    allow_vacation: Annotated[bool | None, Field(alias="allowVacation")] = None
    allow_settings: Annotated[bool | None, Field(alias="allowSettings")] = None
    allow_details: Annotated[bool | None, Field(alias="allowDetails")] = None
    allow_report: Annotated[bool | None, Field(alias="allowReport")] = None
    allow_security: Annotated[bool | None, Field(alias="allowSecurity")] = None
    allow_hierarchy: Annotated[bool | None, Field(alias="allowHierarchy")] = None
    allow_alerts: Annotated[bool | None, Field(alias="allowAlerts")] = None
    allow_manage_account: Annotated[bool | None, Field(alias="allowManageAccount")] = (
        None
    )


class HierarchySet(EcobeeResponseObject):
    set_name: Annotated[str, Field(alias="setName")]
    set_path: Annotated[str | None, Field(alias="setPath")] = None
    children: list[HierarchySet] | None = None
    privileges: list[HierarchyPrivilege] | None = None
    thermostats: list[str] | None = None


class HierarchyUser(EcobeeResponseObject):
    user_name: Annotated[str, Field(alias="userName")]
    first_name: Annotated[str | None, Field(alias="firstName")] = None
    last_name: Annotated[str | None, Field(alias="lastName")] = None
    phone: str | None = None
    last_login: Annotated[str | None, Field(alias="lastLogin")] = None
    active: bool | None = None
    email_alerts: Annotated[bool | None, Field(alias="emailAlerts")] = None


class HouseDetails(EcobeeResponseObject):
    style: str | None = None
    size: int | None = None
    number_of_floors: Annotated[int | None, Field(alias="numberOfFloors")] = None
    number_of_rooms: Annotated[int | None, Field(alias="numberOfRooms")] = None
    number_of_occupants: Annotated[int | None, Field(alias="numberOfOccupants")] = None
    age: int | None = None
    window_efficiency: Annotated[int | None, Field(alias="windowEfficiency")] = None


class LimitSetting(EcobeeResponseObject):
    type: str
    limit: int | None = None
    enabled: bool | None = None
    remind_technician: Annotated[bool | None, Field(alias="remindTechnician")] = None


class Location(EcobeeResponseObject):
    time_zone_offset_minutes: Annotated[
        int | None, Field(alias="timeZoneOffsetMinutes")
    ] = None
    time_zone: Annotated[str | None, Field(alias="timeZone")] = None
    is_daylight_saving: Annotated[bool | None, Field(alias="isDaylightSaving")] = None
    street_address: Annotated[str | None, Field(alias="streetAddress")] = None
    city: str | None = None
    province_state: Annotated[str | None, Field(alias="provinceState")] = None
    country: str | None = None
    postal_code: Annotated[str | None, Field(alias="postalCode")] = None
    phone_number: Annotated[str | None, Field(alias="phoneNumber")] = None
    map_coordinates: Annotated[str | None, Field(alias="mapCoordinates")] = None


class Management(EcobeeResponseObject):
    administrative_contact: Annotated[
        str | None, Field(alias="administrativeContact")
    ] = None
    billing_contact: Annotated[str | None, Field(alias="billingContact")] = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    web: str | None = None
    show_alert_idt: Annotated[bool | None, Field(alias="showAlertIdt")] = None
    show_alert_web: Annotated[bool | None, Field(alias="showAlertWeb")] = None


class MeterReport(EcobeeResponseObject):
    thermostat_identifier: Annotated[
        str | None, Field(alias="thermostatIdentifier")
    ] = None
    meter_list: Annotated[list[MeterReportData] | None, Field(alias="meterList")] = None


class MeterReportData(EcobeeResponseObject):
    meter_type: Annotated[str | None, Field(alias="meterType")] = None
    columns: str | None = None
    data: list[str] | None = None


class NotificationSettings(EcobeeResponseObject):
    email_notifications_enabled: Annotated[
        bool | None, Field(alias="emailNotificationsEnabled")
    ] = None
    equipment: list[EquipmentSetting] | None = None
    general: list[GeneralSetting] | None = None
    limit: list[LimitSetting] | None = None


class Output(EcobeeResponseObject):
    name: str | None = None
    zone: int | None = None
    output_id: Annotated[int | None, Field(alias="outputId")] = None
    type: str
    send_update: Annotated[bool | None, Field(alias="sendUpdate")] = None
    active_closed: Annotated[bool | None, Field(alias="activeClosed")] = None
    activation_time: Annotated[int | None, Field(alias="activationTime")] = None
    deactivation_time: Annotated[int | None, Field(alias="deactivationTime")] = None


class Page(EcobeeResponseObject):
    page: int | None = None
    total_pages: Annotated[int | None, Field(alias="totalPages")] = None
    page_size: Annotated[int | None, Field(alias="pageSize")] = None
    total: int | None = None


class Program(EcobeeResponseObject):
    schedule: list[str]
    climates: list[Climate]
    current_climate_ref: Annotated[str | None, Field(alias="currentClimateRef")] = None


class RemoteSensor(EcobeeResponseObject):
    id: str
    name: str | None = None
    type: str
    code: str | None = None
    in_use: Annotated[bool | None, Field(alias="inUse")] = None
    capability: list[RemoteSensorCapability] | None = None


class RemoteSensorCapability(EcobeeResponseObject):
    id: str
    type: str
    value: str | None = None


class ReportJob(EcobeeResponseObject):
    job_id: Annotated[str | None, Field(alias="jobId")] = None
    status: ReportJobStatus | None = None
    message: str | None = None
    files: list[str] | None = None


class Runtime(EcobeeResponseObject):
    runtime_rev: Annotated[str | None, Field(alias="runtimeRev")] = None
    connected: bool | None = None
    equipment_utilization: Annotated[
        Any | None, Field(alias="equipmentUtilization")
    ] = None
    first_connected: Annotated[str | None, Field(alias="firstConnected")] = None
    connect_date_time: Annotated[str | None, Field(alias="connectDateTime")] = None
    disconnect_date_time: Annotated[str | None, Field(alias="disconnectDateTime")] = (
        None
    )
    last_modified: Annotated[str | None, Field(alias="lastModified")] = None
    last_status_modified: Annotated[str | None, Field(alias="lastStatusModified")] = (
        None
    )
    runtime_date: Annotated[str | None, Field(alias="runtimeDate")] = None
    runtime_interval: Annotated[int | None, Field(alias="runtimeInterval")] = None
    actual_temperature: Annotated[int | None, Field(alias="actualTemperature")] = None
    actual_humidity: Annotated[int | None, Field(alias="actualHumidity")] = None
    raw_temperature: Annotated[int | None, Field(alias="rawTemperature")] = None
    show_icon_mode: Annotated[int | None, Field(alias="showIconMode")] = None
    desired_heat: Annotated[int | None, Field(alias="desiredHeat")] = None
    desired_cool: Annotated[int | None, Field(alias="desiredCool")] = None
    desired_humidity: Annotated[int | None, Field(alias="desiredHumidity")] = None
    desired_dehumidity: Annotated[int | None, Field(alias="desiredDehumidity")] = None
    desired_fan_mode: Annotated[str | None, Field(alias="desiredFanMode")] = None
    desired_heat_range: Annotated[list[int] | None, Field(alias="desiredHeatRange")] = (
        None
    )
    desired_cool_range: Annotated[list[int] | None, Field(alias="desiredCoolRange")] = (
        None
    )


class RuntimeReport(EcobeeResponseObject):
    thermostat_identifier: Annotated[
        str | None, Field(alias="thermostatIdentifier")
    ] = None
    row_count: Annotated[int | None, Field(alias="rowCount")] = None
    row_list: Annotated[list[str] | None, Field(alias="rowList")] = None


class RuntimeSensorMetadata(EcobeeResponseObject):
    sensor_id: Annotated[str | None, Field(alias="sensorId")] = None
    sensor_name: Annotated[str | None, Field(alias="sensorName")] = None
    sensor_type: Annotated[str | None, Field(alias="sensorType")] = None
    sensor_usage: Annotated[str | None, Field(alias="sensorUsage")] = None


class RuntimeSensorReport(EcobeeResponseObject):
    thermostat_identifier: Annotated[
        str | None, Field(alias="thermostatIdentifier")
    ] = None
    sensors: list[RuntimeSensorMetadata] | None = None
    columns: list[str] | None = None
    data: list[str] | None = None


class SecuritySettings(EcobeeResponseObject):
    user_access_code: Annotated[str | None, Field(alias="userAccessCode")] = None
    all_user_access: Annotated[bool | None, Field(alias="allUserAccess")] = None
    program_access: Annotated[bool | None, Field(alias="programAccess")] = None
    details_access: Annotated[bool | None, Field(alias="detailsAccess")] = None
    quick_save_access: Annotated[bool | None, Field(alias="quickSaveAccess")] = None
    vacation_access: Annotated[bool | None, Field(alias="vacationAccess")] = None


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
    sensor_id: Annotated[int | None, Field(alias="sensorId")] = None
    type: str
    usage: str | None = None
    number_of_bits: Annotated[int | None, Field(alias="numberOfBits")] = None
    bconstant: int | None = None
    thermistor_size: Annotated[int | None, Field(alias="thermistorSize")] = None
    temp_correction: Annotated[int | None, Field(alias="tempCorrection")] = None
    gain: int | None = None
    max_voltage: Annotated[int | None, Field(alias="maxVoltage")] = None
    multiplier: int | None = None
    states: list[State] | None = None


class Settings(EcobeeResponseObject):
    display_air_quality: Annotated[bool | None, Field(alias="displayAirQuality")] = None
    hvac_mode: Annotated[str | None, Field(alias="hvacMode")] = None
    last_service_date: Annotated[str | None, Field(alias="lastServiceDate")] = None
    service_remind_me: Annotated[bool | None, Field(alias="serviceRemindMe")] = None
    months_between_service: Annotated[
        int | None, Field(alias="monthsBetweenService")
    ] = None
    remind_me_date: Annotated[str | None, Field(alias="remindMeDate")] = None
    vent: str | None = None
    ventilator_min_on_time: Annotated[
        int | None, Field(alias="ventilatorMinOnTime")
    ] = None
    service_remind_technician: Annotated[
        bool | None, Field(alias="serviceRemindTechnician")
    ] = None
    ei_location: Annotated[str | None, Field(alias="eiLocation")] = None
    cold_temp_alert: Annotated[int | None, Field(alias="coldTempAlert")] = None
    cold_temp_alert_enabled: Annotated[
        bool | None, Field(alias="coldTempAlertEnabled")
    ] = None
    hot_temp_alert: Annotated[int | None, Field(alias="hotTempAlert")] = None
    hot_temp_alert_enabled: Annotated[
        bool | None, Field(alias="hotTempAlertEnabled")
    ] = None
    cool_stages: Annotated[int | None, Field(alias="coolStages")] = None
    heat_stages: Annotated[int | None, Field(alias="heatStages")] = None
    max_set_back: Annotated[int | None, Field(alias="maxSetBack")] = None
    max_set_forward: Annotated[int | None, Field(alias="maxSetForward")] = None
    quick_save_set_back: Annotated[int | None, Field(alias="quickSaveSetBack")] = None
    quick_save_set_forward: Annotated[
        int | None, Field(alias="quickSaveSetForward")
    ] = None
    has_heat_pump: Annotated[bool | None, Field(alias="hasHeatPump")] = None
    has_forced_air: Annotated[bool | None, Field(alias="hasForcedAir")] = None
    has_boiler: Annotated[bool | None, Field(alias="hasBoiler")] = None
    has_humidifier: Annotated[bool | None, Field(alias="hasHumidifier")] = None
    has_erv: Annotated[bool | None, Field(alias="hasErv")] = None
    has_hrv: Annotated[bool | None, Field(alias="hasHrv")] = None
    condensation_avoid: Annotated[bool | None, Field(alias="condensationAvoid")] = None
    use_celsius: Annotated[bool | None, Field(alias="useCelsius")] = None
    use_time_format12: Annotated[bool | None, Field(alias="useTimeFormat12")] = None
    locale: str | None = None
    humidity: str | None = None
    humidifier_mode: Annotated[str | None, Field(alias="humidifierMode")] = None
    backlight_on_intensity: Annotated[
        int | None, Field(alias="backlightOnIntensity")
    ] = None
    backlight_sleep_intensity: Annotated[
        int | None, Field(alias="backlightSleepIntensity")
    ] = None
    backlight_off_time: Annotated[int | None, Field(alias="backlightOffTime")] = None
    sound_tick_volume: Annotated[int | None, Field(alias="soundTickVolume")] = None
    sound_alert_volume: Annotated[int | None, Field(alias="soundAlertVolume")] = None
    compressor_protection_min_time: Annotated[
        int | None, Field(alias="compressorProtectionMinTime")
    ] = None
    compressor_protection_min_temp: Annotated[
        int | None, Field(alias="compressorProtectionMinTemp")
    ] = None
    stage1_heating_differential_temp: Annotated[
        int | None, Field(alias="stage1HeatingDifferentialTemp")
    ] = None
    stage1_cooling_differential_temp: Annotated[
        int | None, Field(alias="stage1CoolingDifferentialTemp")
    ] = None
    stage1_heating_dissipation_time: Annotated[
        int | None, Field(alias="stage1HeatingDissipationTime")
    ] = None
    stage1_cooling_dissipation_time: Annotated[
        int | None, Field(alias="stage1CoolingDissipationTime")
    ] = None
    heat_pump_reversal_on_cool: Annotated[
        bool | None, Field(alias="heatPumpReversalOnCool")
    ] = None
    fan_control_required: Annotated[bool | None, Field(alias="fanControlRequired")] = (
        None
    )
    fan_min_on_time: Annotated[int | None, Field(alias="fanMinOnTime")] = None
    heat_cool_min_delta: Annotated[int | None, Field(alias="heatCoolMinDelta")] = None
    temp_correction: Annotated[int | None, Field(alias="tempCorrection")] = None
    hold_action: Annotated[str | None, Field(alias="holdAction")] = None
    heat_pump_ground_water: Annotated[
        bool | None, Field(alias="heatPumpGroundWater")
    ] = None
    has_electric: Annotated[bool | None, Field(alias="hasElectric")] = None
    has_dehumidifier: Annotated[bool | None, Field(alias="hasDehumidifier")] = None
    dehumidifier_mode: Annotated[str | None, Field(alias="dehumidifierMode")] = None
    dehumidifier_level: Annotated[int | None, Field(alias="dehumidifierLevel")] = None
    dehumidify_with_a_c: Annotated[bool | None, Field(alias="dehumidifyWithAC")] = None
    dehumidify_overcool_offset: Annotated[
        int | None, Field(alias="dehumidifyOvercoolOffset")
    ] = None
    auto_heat_cool_feature_enabled: Annotated[
        bool | None, Field(alias="autoHeatCoolFeatureEnabled")
    ] = None
    wifi_offline_alert: Annotated[bool | None, Field(alias="wifiOfflineAlert")] = None
    heat_min_temp: Annotated[int | None, Field(alias="heatMinTemp")] = None
    heat_max_temp: Annotated[int | None, Field(alias="heatMaxTemp")] = None
    cool_min_temp: Annotated[int | None, Field(alias="coolMinTemp")] = None
    cool_max_temp: Annotated[int | None, Field(alias="coolMaxTemp")] = None
    heat_range_high: Annotated[int | None, Field(alias="heatRangeHigh")] = None
    heat_range_low: Annotated[int | None, Field(alias="heatRangeLow")] = None
    cool_range_high: Annotated[int | None, Field(alias="coolRangeHigh")] = None
    cool_range_low: Annotated[int | None, Field(alias="coolRangeLow")] = None
    user_access_code: Annotated[str | None, Field(alias="userAccessCode")] = None
    user_access_setting: Annotated[int | None, Field(alias="userAccessSetting")] = None
    aux_runtime_alert: Annotated[int | None, Field(alias="auxRuntimeAlert")] = None
    aux_outdoor_temp_alert: Annotated[
        int | None, Field(alias="auxOutdoorTempAlert")
    ] = None
    aux_max_outdoor_temp: Annotated[int | None, Field(alias="auxMaxOutdoorTemp")] = None
    aux_runtime_alert_notify: Annotated[
        bool | None, Field(alias="auxRuntimeAlertNotify")
    ] = None
    aux_outdoor_temp_alert_notify: Annotated[
        bool | None, Field(alias="auxOutdoorTempAlertNotify")
    ] = None
    aux_runtime_alert_notify_technician: Annotated[
        bool | None, Field(alias="auxRuntimeAlertNotifyTechnician")
    ] = None
    aux_outdoor_temp_alert_notify_technician: Annotated[
        bool | None, Field(alias="auxOutdoorTempAlertNotifyTechnician")
    ] = None
    disable_pre_heating: Annotated[bool | None, Field(alias="disablePreHeating")] = None
    disable_pre_cooling: Annotated[bool | None, Field(alias="disablePreCooling")] = None
    installer_code_required: Annotated[
        bool | None, Field(alias="installerCodeRequired")
    ] = None
    dr_accept: Annotated[str | None, Field(alias="drAccept")] = None
    is_rental_property: Annotated[bool | None, Field(alias="isRentalProperty")] = None
    use_zone_controller: Annotated[bool | None, Field(alias="useZoneController")] = None
    random_start_delay_cool: Annotated[
        int | None, Field(alias="randomStartDelayCool")
    ] = None
    random_start_delay_heat: Annotated[
        int | None, Field(alias="randomStartDelayHeat")
    ] = None
    humidity_high_alert: Annotated[int | None, Field(alias="humidityHighAlert")] = None
    humidity_low_alert: Annotated[int | None, Field(alias="humidityLowAlert")] = None
    disable_heat_pump_alerts: Annotated[
        bool | None, Field(alias="disableHeatPumpAlerts")
    ] = None
    disable_alerts_on_idt: Annotated[bool | None, Field(alias="disableAlertsOnIdt")] = (
        None
    )
    humidity_alert_notify: Annotated[
        bool | None, Field(alias="humidityAlertNotify")
    ] = None
    humidity_alert_notify_technician: Annotated[
        bool | None, Field(alias="humidityAlertNotifyTechnician")
    ] = None
    temp_alert_notify: Annotated[bool | None, Field(alias="tempAlertNotify")] = None
    temp_alert_notify_technician: Annotated[
        bool | None, Field(alias="tempAlertNotifyTechnician")
    ] = None
    monthly_electricity_bill_limit: Annotated[
        int | None, Field(alias="monthlyElectricityBillLimit")
    ] = None
    enable_electricity_bill_alert: Annotated[
        bool | None, Field(alias="enableElectricityBillAlert")
    ] = None
    enable_projected_electricity_bill_alert: Annotated[
        bool | None, Field(alias="enableProjectedElectricityBillAlert")
    ] = None
    electricity_billing_day_of_month: Annotated[
        int | None, Field(alias="electricityBillingDayOfMonth")
    ] = None
    electricity_bill_cycle_months: Annotated[
        int | None, Field(alias="electricityBillCycleMonths")
    ] = None
    electricity_bill_start_month: Annotated[
        int | None, Field(alias="electricityBillStartMonth")
    ] = None
    ventilator_min_on_time_home: Annotated[
        int | None, Field(alias="ventilatorMinOnTimeHome")
    ] = None
    ventilator_min_on_time_away: Annotated[
        int | None, Field(alias="ventilatorMinOnTimeAway")
    ] = None
    backlight_off_during_sleep: Annotated[
        bool | None, Field(alias="backlightOffDuringSleep")
    ] = None
    auto_away: Annotated[bool | None, Field(alias="autoAway")] = None
    smart_circulation: Annotated[bool | None, Field(alias="smartCirculation")] = None
    follow_me_comfort: Annotated[bool | None, Field(alias="followMeComfort")] = None
    ventilator_type: Annotated[str | None, Field(alias="ventilatorType")] = None
    is_ventilator_timer_on: Annotated[
        bool | None, Field(alias="isVentilatorTimerOn")
    ] = None
    ventilator_off_date_time: Annotated[
        str | None, Field(alias="ventilatorOffDateTime")
    ] = None
    has_u_v_filter: Annotated[bool | None, Field(alias="hasUVFilter")] = None
    cooling_lockout: Annotated[bool | None, Field(alias="coolingLockout")] = None
    ventilator_free_cooling: Annotated[
        bool | None, Field(alias="ventilatorFreeCooling")
    ] = None
    dehumidify_when_heating: Annotated[
        bool | None, Field(alias="dehumidifyWhenHeating")
    ] = None
    ventilator_dehumidify: Annotated[
        bool | None, Field(alias="ventilatorDehumidify")
    ] = None
    group_ref: Annotated[str | None, Field(alias="groupRef")] = None
    group_name: Annotated[str | None, Field(alias="groupName")] = None
    group_setting: Annotated[int | None, Field(alias="groupSetting")] = None
    fan_speed: Annotated[str | None, Field(alias="fanSpeed")] = None


class State(EcobeeResponseObject):
    max_value: Annotated[int | None, Field(alias="maxValue")] = None
    min_value: Annotated[int | None, Field(alias="minValue")] = None
    type: str
    actions: list[Action] | None = None


class Status(EcobeeResponseObject):
    code: int | None = None
    message: str | None = None


class Technician(EcobeeResponseObject):
    contractor_ref: Annotated[str | None, Field(alias="contractorRef")] = None
    name: str | None = None
    phone: str | None = None
    street_address: Annotated[str | None, Field(alias="streetAddress")] = None
    city: str | None = None
    province_state: Annotated[str | None, Field(alias="provinceState")] = None
    country: str | None = None
    postal_code: Annotated[str | None, Field(alias="postalCode")] = None
    email: str | None = None
    web: str | None = None


class Thermostat(EcobeeResponseObject):
    identifier: str
    name: str | None = None
    thermostat_rev: Annotated[str | None, Field(alias="thermostatRev")] = None
    is_registered: Annotated[bool | None, Field(alias="isRegistered")] = None
    model_number: Annotated[str | None, Field(alias="modelNumber")] = None
    brand: str | None = None
    features: str | None = None
    last_modified: Annotated[str | None, Field(alias="lastModified")] = None
    thermostat_time: Annotated[str | None, Field(alias="thermostatTime")] = None
    utc_time: Annotated[str | None, Field(alias="utcTime")] = None
    audio: Audio | None = None
    capabilities: Capabilities | None = None
    alerts: list[Alert] | None = None
    reminders: list[Any] | None = None
    settings: Settings | None = None
    runtime: Runtime | None = None
    extended_runtime: Annotated[
        ExtendedRuntime | None, Field(alias="extendedRuntime")
    ] = None
    devices: list[Device] | None = None
    location: Location | None = None
    technician: Technician | None = None
    utility: Utility | None = None
    management: Management | None = None
    weather: Weather | None = None
    events: list[Event] | None = None
    program: Program | None = None
    house_details: Annotated[HouseDetails | None, Field(alias="houseDetails")] = None
    oem_cfg: Annotated[Any | None, Field(alias="oemCfg")] = None
    equipment_status: Annotated[str | None, Field(alias="equipmentStatus")] = None
    notification_settings: Annotated[
        NotificationSettings | None, Field(alias="notificationSettings")
    ] = None
    privacy: Any | None = None
    version: Version | None = None
    security_settings: Annotated[
        SecuritySettings | None, Field(alias="securitySettings")
    ] = None
    filter_subscription: Annotated[Any | None, Field(alias="filterSubscription")] = None
    remote_sensors: Annotated[
        list[RemoteSensor] | None, Field(alias="remoteSensors")
    ] = None


class TimeOfUse(EcobeeResponseObject):
    feature_state: Annotated[str | None, Field(alias="featureState")] = None
    savings: str | None = None


class User(EcobeeResponseObject):
    user_name: Annotated[str, Field(alias="userName")]
    display_name: Annotated[str | None, Field(alias="displayName")] = None
    first_name: Annotated[str | None, Field(alias="firstName")] = None
    last_name: Annotated[str | None, Field(alias="lastName")] = None
    honorific: str | None = None
    register_date: Annotated[str | None, Field(alias="registerDate")] = None
    register_time: Annotated[str | None, Field(alias="registerTime")] = None
    default_thermostat_identifier: Annotated[
        str | None, Field(alias="defaultThermostatIdentifier")
    ] = None
    management_ref: Annotated[str | None, Field(alias="managementRef")] = None
    utility_ref: Annotated[str | None, Field(alias="utilityRef")] = None
    support_ref: Annotated[str | None, Field(alias="supportRef")] = None
    phone_number: Annotated[str | None, Field(alias="phoneNumber")] = None
    utility_time_zone: Annotated[str | None, Field(alias="utilityTimeZone")] = None
    management_time_zone: Annotated[str | None, Field(alias="managementTimeZone")] = (
        None
    )
    is_residential: Annotated[bool | None, Field(alias="isResidential")] = None
    is_developer: Annotated[bool | None, Field(alias="isDeveloper")] = None
    is_management: Annotated[bool | None, Field(alias="isManagement")] = None
    is_utility: Annotated[bool | None, Field(alias="isUtility")] = None
    is_contractor: Annotated[bool | None, Field(alias="isContractor")] = None


class Utility(EcobeeResponseObject):
    id: str | None = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    web: str | None = None


class Version(EcobeeResponseObject):
    thermostat_firmware_version: Annotated[
        str | None, Field(alias="thermostatFirmwareVersion")
    ] = None


class VoiceEngine(EcobeeResponseObject):
    name: str | None = None
    enabled: bool | None = None


class Weather(EcobeeResponseObject):
    timestamp: str | None = None
    weather_station: Annotated[str | None, Field(alias="weatherStation")] = None
    forecasts: list[WeatherForecast] | None = None


class WeatherForecast(EcobeeResponseObject):
    weather_symbol: Annotated[int | None, Field(alias="weatherSymbol")] = None
    date_time: Annotated[str | None, Field(alias="dateTime")] = None
    condition: str | None = None
    temperature: int | None = None
    pressure: int | None = None
    relative_humidity: Annotated[int | None, Field(alias="relativeHumidity")] = None
    dewpoint: int | None = None
    visibility: int | None = None
    wind_speed: Annotated[int | None, Field(alias="windSpeed")] = None
    wind_gust: Annotated[int | None, Field(alias="windGust")] = None
    wind_direction: Annotated[str | None, Field(alias="windDirection")] = None
    wind_bearing: Annotated[int | None, Field(alias="windBearing")] = None
    pop: int | None = None
    temp_high: Annotated[int | None, Field(alias="tempHigh")] = None
    temp_low: Annotated[int | None, Field(alias="tempLow")] = None
    sky: int | None = None


class EcobeeStatusResponse(EcobeeResponseObject):
    status: Status


class EcobeeAuthorizeResponse(EcobeeResponseObject):
    ecobee_pin: Annotated[str, Field(alias="ecobeePin")]
    code: str
    scope: str
    expires_in: int
    interval: int


class EcobeeCreateRuntimeReportJobResponse(EcobeeStatusResponse):
    job_id: Annotated[str, Field(alias="jobId")]
    job_status: Annotated[ReportJobStatus, Field(alias="jobStatus")]
    status: Status


class EcobeeErrorResponse(EcobeeResponseObject):
    error: str
    error_description: str
    error_uri: str


class EcobeeGroupsResponse(EcobeeStatusResponse):
    groups: list[Group]
    status: Status


class EcobeeIssueDemandResponsesResponse(EcobeeStatusResponse):
    demand_response_ref: Annotated[str, Field(alias="demandResponseRef")]
    status: Status


class EcobeeListDemandResponsesResponse(EcobeeStatusResponse):
    demand_response_list: Annotated[list[DemandResponse], Field(alias="drList")]
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
    report_list: Annotated[list[MeterReport], Field(alias="reportList")]
    status: Status


class EcobeeRuntimeReportsResponse(EcobeeStatusResponse):
    start_date: Annotated[str, Field(alias="startDate")]
    start_interval: Annotated[int, Field(alias="startInterval")]
    end_date: Annotated[str, Field(alias="endDate")]
    end_interval: Annotated[int, Field(alias="endInterval")]
    columns: str
    report_list: Annotated[list[RuntimeReport], Field(alias="reportList")]
    sensor_list: Annotated[list[RuntimeSensorReport], Field(alias="sensorList")]
    status: Status


class EcobeeThermostatResponse(EcobeeStatusResponse):
    page: Page
    thermostat_list: Annotated[list[Thermostat], Field(alias="thermostatList")]
    status: Status


class EcobeeThermostatsSummaryResponse(EcobeeStatusResponse):
    revision_list: Annotated[list[str], Field(alias="revisionList")]
    thermostat_count: Annotated[int, Field(alias="thermostatCount")]
    status_list: Annotated[list[str], Field(alias="statusList")]
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
