# Pyecobee

A Python implementation of the [ecobee API](https://www.ecobee.com/home/developer/api/introduction/index.shtml).

Pyecobee is a simple, elegant, and object oriented implementation of the ecobee API in Python. Requests and
responses are Python objects: Pyecobee serializes them to and from the JSON the ecobee API expects, so you never
have to build or parse JSON yourself.

Requires Python 3.12 or newer.

- [Installation](#installation)
- [Quick start](#quick-start)
- [Requests and responses](#requests-and-responses)
- [General usage](#general-usage)
- [Authorization and token requests](#authorization-and-token-requests)
- [Thermostat requests](#thermostat-requests)
- [Report requests](#report-requests)
- [Group requests](#group-requests)
- [Hierarchy set requests](#hierarchy-set-requests)
- [Hierarchy user requests](#hierarchy-user-requests)
- [Hierarchy thermostat requests](#hierarchy-thermostat-requests)
- [Utility requests](#utility-requests)
- [Runtime report job requests](#runtime-report-job-requests)
- [Thermostat functions](#thermostat-functions)
- [Credentials](#credentials)
- [Token renewal](#token-renewal)
- [Date and time handling](#date-and-time-handling)
- [Exception handling](#exception-handling)
- [Development](#development)

> [!WARNING]
> Pyecobee has been tested with an ecobee Smart Si. The following methods have not been tested, though they should
> work. Please open an [issue](https://github.com/sherif-fanous/Pyecobee/issues), or better still a
> [pull request](https://github.com/sherif-fanous/Pyecobee/pulls), if you hit a problem with any of them.
>
> - `control_plug`: requires an ecobee smart plug
> - `reset_preferences`: wipes a thermostat's settings
> - `set_occupied`: requires an EMS thermostat
> - `unlink_voice_engine`: requires a thermostat with voice control
> - `update_sensor`: requires an ecobee3 or ecobee4 thermostat
> - All hierarchy requests, accessible to EMS and Utility accounts only: `list_hierarchy_sets`,
>   `list_hierarchy_users`, `add_hierarchy_set`, `remove_hierarchy_set`, `rename_hierarchy_set`,
>   `move_hierarchy_set`, `add_hierarchy_users`, `remove_hierarchy_users`, `unregister_hierarchy_users`,
>   `update_hierarchy_users`, `register_hierarchy_thermostats`, `unregister_hierarchy_thermostats`,
>   `move_hierarchy_thermostats`, `assign_hierarchy_thermostats`
> - All utility requests, accessible to Utility accounts only: `list_demand_responses`, `issue_demand_response`,
>   `cancel_demand_response`, `issue_demand_managements`
> - All runtime report job requests, accessible to Utility accounts only: `create_runtime_report_job`,
>   `list_runtime_report_job_status`, `cancel_runtime_report_job`

> [!NOTE]
> ecobee currently returns 404 for the object definitions of `ECPDemandResponse` and `EquipmentUtilization`.
> Responses stay forward compatible because unknown fields are ignored, and `Runtime.equipment_utilization` is kept
> as an untyped value until ecobee publishes its shape.

Any ecobee API keys and authorization, access or refresh tokens in the examples below are fake.

## Installation

```bash
pip install pyecobee
```

## Quick start

```python
from pyecobee import EcobeeService, Selection, SelectionType, Tokens

ecobee_service = EcobeeService(
    "My Thermostat",
    "jiNXJ2Q6dyeAPXxy4HsFGUp1nK94C9VF",
    Tokens(),  # or the credentials you stored last time
    save_tokens,  # called whenever new credentials are issued
)

# One-time authorization: display the PIN, register the app at ecobee.com, then request tokens.
authorize_response = ecobee_service.authorize()
print(f"Enter this PIN at ecobee.com => {authorize_response.ecobee_pin}")
input("Press Enter once the app is authorized...")
ecobee_service.request_tokens()

thermostat_response = ecobee_service.request_thermostats(
    Selection(
        selection_type=SelectionType.REGISTERED,
        selection_match="",
        include_runtime=True,
    )
)
thermostat = thermostat_response.thermostat_list[0]
print(thermostat.name, thermostat.runtime.actual_temperature)
```

Pyecobee hands every new set of credentials to the callback and renews expired access tokens on its own. See
[Credentials](#credentials).

## Requests and responses

### Building a request

Request models accept Python field names and serialize to ecobee's camelCase field names. Use enum members for enum
fields.

```python
from pyecobee import Selection, SelectionType

selection = Selection(
    selection_type=SelectionType.THERMOSTATS,
    selection_match="123456789012",
    include_runtime=True,
)

assert selection.to_api_dict() == {
    "selectionType": "thermostats",
    "selectionMatch": "123456789012",
    "includeRuntime": True,
}
```

### Processing a response

Service methods deserialize responses into typed models. Access Python attributes, or use `model_dump()` when an
alias-based JSON-compatible mapping is needed.

```python
response = ecobee_service.request_thermostats(selection)
response.status.code  # 0 indicates success

thermostat = response.thermostat_list[0]
payload = response.model_dump(by_alias=True, exclude_none=True, mode="json")
```

Response models ignore fields that ecobee adds after this release, including fields within nested objects.

Every model provides `pretty_format()` for alias-based diagnostic output, alongside the usual `repr()`:

```pycon
>>> repr(authorize_response)
"EcobeeAuthorizeResponse(ecobee_pin='bv29', code='...', scope='smartWrite', expires_in=9, interval=30)"

>>> authorize_response.pretty_format()
"EcobeeAuthorizeResponse({'code': '...', 'ecobeePin': 'bv29', ...})"
```

## General usage

The `EcobeeService` class provides the ecobee API implementation. To use Pyecobee:

1. Import the models you need.
2. Instantiate an `EcobeeService` object.
3. Complete the authorization sequence if required (`authorize` then `request_tokens`).
4. Refresh the tokens when they expire (`refresh_tokens`).
5. Invoke the ecobee API requests and functions you need.

Pyecobee ships with docstrings throughout. Use `dir()` and `help()` to explore:

```pycon
>>> from pyecobee import EcobeeService
>>> dir(EcobeeService)
>>> help(EcobeeService)
```

### Import the models

```python
from pyecobee import EcobeeService, Selection, SelectionType, Tokens
from pyecobee.objects.thermostat import Thermostat

# Import other models, enums, and exceptions by their explicit names.
```

### Instantiate an EcobeeService object

```python
ecobee_service = EcobeeService(
    "My Thermostat",  # a label of your choosing
    "jiNXJ2Q6dyeAPXxy4HsFGUp1nK94C9VF",  # your application key
    Tokens(),  # the credentials you hold, if any
    save_tokens,  # where to put the credentials ecobee issues
)
```

Every parameter is required. You pass the credentials you hold as `tokens` and get back every new set through
`on_tokens_changed`, because the ecobee API requires an application to store what it is issued and replaces the
refresh token every time it issues one.

## Authorization and token requests

Each snippet below assumes a module-level `logger = logging.getLogger(__name__)`.

### Authorize

```python
authorize_response = ecobee_service.authorize()
logger.info(authorize_response.pretty_format())
logger.info(f"Authorization Token => {ecobee_service.authorization_token}")
```

A successful invocation of `authorize()` returns an `EcobeeAuthorizeResponse` instance.

### Request tokens

```python
token_response = ecobee_service.request_tokens()
logger.info(token_response.pretty_format())
logger.info(
    f"Access Token => {ecobee_service.access_token}\n"
    f"Access Token Expires On => {ecobee_service.access_token_expires_on}\n"
    f"Refresh Token => {ecobee_service.refresh_token}\n"
    f"Refresh Token Expires On => {ecobee_service.refresh_token_expires_on}"
)
```

A successful invocation of `request_tokens()` returns an `EcobeeTokensResponse` instance.

### Refresh tokens

Renewal is automatic, so this is only needed to renew on your own schedule. See
[Token renewal](#token-renewal).

```python
token_response = ecobee_service.refresh_tokens()
logger.info(token_response.pretty_format())
```

A successful invocation of `refresh_tokens()` returns an `EcobeeTokensResponse` instance.

## Thermostat requests

### Request thermostat summary

```python
thermostat_summary_response = ecobee_service.request_thermostats_summary(
    selection=Selection(
        selection_type=SelectionType.REGISTERED,
        selection_match="",
        include_equipment_status=True,
    )
)
logger.info(thermostat_summary_response.pretty_format())
```

A successful invocation of `request_thermostats_summary()` returns an `EcobeeThermostatsSummaryResponse` instance.

### Request thermostats

```python
# Only set the include options you need to True. Most are set to True here for illustrative purposes only.
selection = Selection(
    selection_type=SelectionType.REGISTERED,
    selection_match="",
    include_alerts=True,
    include_audio=True,
    include_capabilities=True,
    include_device=True,
    include_energy=True,
    include_equipment_status=True,
    include_events=True,
    include_extended_runtime=True,
    include_house_details=True,
    include_location=True,
    include_management=True,
    include_notification_settings=True,
    include_oem_cfg=False,
    include_privacy=False,
    include_program=True,
    include_reminders=True,
    include_runtime=True,
    include_security_settings=False,
    include_sensors=True,
    include_settings=True,
    include_technician=True,
    include_utility=True,
    include_version=True,
    include_weather=True,
)
thermostat_response = ecobee_service.request_thermostats(selection)
logger.info(thermostat_response.pretty_format())
assert thermostat_response.status.code == 0, (
    f"Failure while executing request_thermostats:\n{thermostat_response.pretty_format()}"
)
```

A successful invocation of `request_thermostats()` returns an `EcobeeThermostatResponse` instance.

### Update thermostat

```python
from pyecobee import Function, Selection, SelectionType, Settings, Thermostat

update_thermostat_response = ecobee_service.update_thermostats(
    selection=Selection(selection_type=SelectionType.REGISTERED, selection_match=""),
    thermostat=Thermostat(
        identifier="123456789012", settings=Settings(hvac_mode="off")
    ),
    functions=[Function(type="deleteVacation", params={"name": "My vacation"})],
)
logger.info(update_thermostat_response.pretty_format())
assert update_thermostat_response.status.code == 0, (
    f"Failure while executing update_thermostats:\n{update_thermostat_response.pretty_format()}"
)
```

A successful invocation of `update_thermostats()` returns an `EcobeeStatusResponse` instance.

## Report requests

### Meter report

```python
from datetime import datetime
from zoneinfo import ZoneInfo

eastern = ZoneInfo("America/New_York")
meter_reports_response = ecobee_service.request_meter_reports(
    selection=Selection(
        selection_type=SelectionType.THERMOSTATS,
        selection_match="123456789012",
    ),
    start_date_time=datetime(2013, 4, 4, 0, 0, 0, tzinfo=eastern),
    end_date_time=datetime(2013, 4, 4, 23, 59, 0, tzinfo=eastern),
)
logger.info(meter_reports_response.pretty_format())
assert meter_reports_response.status.code == 0, (
    f"Failure while executing request_meter_reports:\n{meter_reports_response.pretty_format()}"
)
```

A successful invocation of `request_meter_reports()` returns an `EcobeeMeterReportsResponse` instance.

### Runtime report

```python
eastern = ZoneInfo("America/New_York")
runtime_reports_response = ecobee_service.request_runtime_reports(
    selection=Selection(
        selection_type=SelectionType.THERMOSTATS,
        selection_match="123456789012",
    ),
    start_date_time=datetime(2010, 1, 1, 0, 0, 0, tzinfo=eastern),
    end_date_time=datetime(2010, 1, 2, 0, 0, 0, tzinfo=eastern),
    columns=(
        "auxHeat1,auxHeat2,auxHeat3,compCool1,compCool2,compHeat1,compHeat2,dehumidifier,dmOffset,"
        "economizer,fan,humidifier,hvacMode,outdoorHumidity,outdoorTemp,sky,ventilator,wind,zoneAveTemp,"
        "zoneCalendarEvent,zoneClimate,zoneCoolTemp,zoneHeatTemp,zoneHumidity,zoneHumidityHigh,"
        "zoneHumidityLow,zoneHvacMode,zoneOccupancy"
    ),
)
logger.info(runtime_reports_response.pretty_format())
assert runtime_reports_response.status.code == 0, (
    f"Failure while executing request_runtime_reports:\n{runtime_reports_response.pretty_format()}"
)
```

A successful invocation of `request_runtime_reports()` returns an `EcobeeRuntimeReportsResponse` instance.

## Group requests

### Request groups

```python
group_response = ecobee_service.request_groups(
    selection=Selection(selection_type=SelectionType.REGISTERED, selection_match="")
)
logger.info(group_response.pretty_format())
assert group_response.status.code == 0, (
    f"Failure while executing request_groups:\n{group_response.pretty_format()}"
)
```

A successful invocation of `request_groups()` returns an `EcobeeGroupsResponse` instance.

### Update groups

```python
from pyecobee import Group

# Create groups
group_response = ecobee_service.update_groups(
    selection=Selection(selection_type=SelectionType.REGISTERED, selection_match=""),
    groups=[
        Group(
            group_ref="3d03a26fd80001",
            group_name="ground_floor",
            synchronize_alerts=True,
            synchronize_vacation=True,
            thermostats=["123456789101"],
        ),
        Group(
            group_ref="3bb5a91b180001",
            group_name="first_floor",
            synchronize_reset=True,
            synchronize_vacation=True,
            thermostats=["123456789102"],
        ),
    ],
)

# Update a group
group_response = ecobee_service.update_groups(
    selection=Selection(selection_type=SelectionType.REGISTERED, selection_match=""),
    groups=[
        Group(
            group_name="ground_floor",
            group_ref="3d03a26fd80001",
            synchronize_system_mode=True,
        )
    ],
)

# Delete a group by setting its thermostats to an empty list
group_response = ecobee_service.update_groups(
    selection=Selection(selection_type=SelectionType.REGISTERED, selection_match=""),
    groups=[
        Group(group_name="ground_floor", group_ref="3d03a26fd80001", thermostats=[])
    ],
)
logger.info(group_response.pretty_format())
assert group_response.status.code == 0, (
    f"Failure while executing update_groups:\n{group_response.pretty_format()}"
)
```

A successful invocation of `update_groups()` returns an `EcobeeGroupsResponse` instance.

## Hierarchy set requests

### List hierarchy sets

```python
list_hierarchy_sets_response = ecobee_service.list_hierarchy_sets(
    set_path="/",
    recursive=True,
    include_privileges=True,
    include_thermostats=True,
)
logger.info(list_hierarchy_sets_response.pretty_format())
assert list_hierarchy_sets_response.status.code == 0, (
    f"Failure while executing list_hierarchy_sets:\n{list_hierarchy_sets_response.pretty_format()}"
)
```

A successful invocation of `list_hierarchy_sets()` returns an `EcobeeListHierarchySetsResponse` instance.

### Add hierarchy set

```python
add_hierarchy_set_response = ecobee_service.add_hierarchy_set(
    set_name="NewSet", parent_path="/"
)
```

### Remove hierarchy set

```python
remove_hierarchy_set_response = ecobee_service.remove_hierarchy_set(set_path="/NewSet")
```

### Rename hierarchy set

```python
rename_hierarchy_set_response = ecobee_service.rename_hierarchy_set(
    set_path="/NewSet", new_name="ToRename"
)
```

### Move hierarchy set

```python
move_hierarchy_set_response = ecobee_service.move_hierarchy_set(
    set_path="/ToMove", to_path="MainNode"
)
```

A successful invocation of `add_hierarchy_set()`, `remove_hierarchy_set()`, `rename_hierarchy_set()` or
`move_hierarchy_set()` returns an `EcobeeStatusResponse` instance.

## Hierarchy user requests

### List hierarchy users

```python
list_hierarchy_users_response = ecobee_service.list_hierarchy_users(
    set_path="/",
    recursive=True,
    include_privileges=True,
)
logger.info(list_hierarchy_users_response.pretty_format())
assert list_hierarchy_users_response.status.code == 0, (
    f"Failure while executing list_hierarchy_users:\n{list_hierarchy_users_response.pretty_format()}"
)
```

A successful invocation of `list_hierarchy_users()` returns an `EcobeeListHierarchyUsersResponse` instance.

### Add hierarchy users

```python
from pyecobee import HierarchyPrivilege, HierarchyUser

add_hierarchy_users_response = ecobee_service.add_hierarchy_users(
    users=[
        HierarchyUser(user_name="new@user1.com", first_name="User", last_name="1"),
        HierarchyUser(user_name="new@user2.com", first_name="User", last_name="2"),
    ],
    privileges=[
        HierarchyPrivilege(
            set_path="/MainNode", user_name="new@user1.com", allow_view=True
        ),
        HierarchyPrivilege(
            set_path="/OtherNode", user_name="new@user1.com", allow_view=True
        ),
    ],
)
logger.info(add_hierarchy_users_response.pretty_format())
assert add_hierarchy_users_response.status.code == 0, (
    f"Failure while executing add_hierarchy_users:\n{add_hierarchy_users_response.pretty_format()}"
)
```

### Remove hierarchy users

```python
remove_hierarchy_users_response = ecobee_service.remove_hierarchy_users(
    set_path="/",
    users=[
        HierarchyUser(user_name="todelete@hierarchy.com"),
        HierarchyUser(user_name="todelete2@hierarchy.com"),
    ],
)
```

### Unregister hierarchy users

```python
unregister_hierarchy_users_response = ecobee_service.unregister_hierarchy_users(
    users=[
        HierarchyUser(user_name="todelete@hierarchy.com"),
        HierarchyUser(user_name="todelete2@hierarchy.com"),
    ]
)
```

### Update hierarchy users

```python
update_hierarchy_users_response = ecobee_service.update_hierarchy_users(
    users=[
        HierarchyUser(
            user_name="user1@update.com",
            first_name="Updated",
            last_name="User",
            phone="222-333-4444",
            email_alerts=False,
        )
    ],
    privileges=[
        HierarchyPrivilege(
            set_path="/MainNode", user_name="user1@update.com", allow_view=True
        ),
        HierarchyPrivilege(
            set_path="/MainNode", user_name="user2@update.com", allow_view=True
        ),
        HierarchyPrivilege(
            set_path="/OtherNode", user_name="user2@update.com", allow_view=True
        ),
    ],
)
```

A successful invocation of `add_hierarchy_users()`, `remove_hierarchy_users()`, `unregister_hierarchy_users()` or
`update_hierarchy_users()` returns an `EcobeeStatusResponse` instance.

## Hierarchy thermostat requests

### Register thermostats

```python
register_hierarchy_thermostats_response = ecobee_service.register_hierarchy_thermostats(
    set_path="/OtherNode",
    thermostats="123456789012,123456789013",
)
```

### Unregister thermostats

```python
unregister_hierarchy_thermostats_response = (
    ecobee_service.unregister_hierarchy_thermostats(
        thermostats="123456789012,123456789013"
    )
)
```

### Move thermostats

```python
move_hierarchy_thermostats_response = ecobee_service.move_hierarchy_thermostats(
    set_path="/MainNode",
    to_path="/OtherNode",
    thermostats="123456789012,123456789013",
)
```

### Assign thermostats

```python
assign_hierarchy_thermostats_response = ecobee_service.assign_hierarchy_thermostats(
    set_path="/MainNode",
    thermostats="123456789012,123456789013",
)
```

A successful invocation of any hierarchy thermostat request returns an `EcobeeStatusResponse` instance.

## Utility requests

### List demand responses

```python
list_demand_responses_response = ecobee_service.list_demand_responses()
logger.info(list_demand_responses_response.pretty_format())
assert list_demand_responses_response.status.code == 0, (
    f"Failure while executing list_demand_responses:\n{list_demand_responses_response.pretty_format()}"
)
```

A successful invocation of `list_demand_responses()` returns an `EcobeeListDemandResponsesResponse` instance.

### Issue demand response

```python
from pyecobee import DemandResponse, Event

issue_demand_response_response = ecobee_service.issue_demand_response(
    selection=Selection(
        selection_type=SelectionType.MANAGEMENT_SET, selection_match="/"
    ),
    demand_response=DemandResponse(
        name="myDR",
        message="This is a DR!",
        event=Event(
            type="useEndTime",
            name="apiDR",
            start_date="2011-01-09",
            start_time="11:37:18",
            end_date="2011-01-10",
            end_time="11:37:18",
            cool_hold_temp=790,
            heat_hold_temp=790,
            is_temperature_absolute=True,
        ),
    ),
)
logger.info(issue_demand_response_response.pretty_format())
assert issue_demand_response_response.status.code == 0, (
    f"Failure while executing issue_demand_response:\n{issue_demand_response_response.pretty_format()}"
)
```

A successful invocation of `issue_demand_response()` returns an `EcobeeIssueDemandResponsesResponse` instance.

### Cancel demand response

```python
cancel_demand_response_response = ecobee_service.cancel_demand_response(
    demand_response_ref="c253a12e0b3c3c93800095"
)
```

A successful invocation of `cancel_demand_response()` returns an `EcobeeStatusResponse` instance.

### Issue demand managements

```python
from pyecobee import DemandManagement

issue_demand_managements_response = ecobee_service.issue_demand_managements(
    selection=Selection(
        selection_type=SelectionType.MANAGEMENT_SET, selection_match="/"
    ),
    demand_managements=[
        DemandManagement(
            date="2012-01-01",
            hour=5,
            temp_offsets=[20, 20, 20, 0, 0, 0, 0, -20, -20, -20, 0, 0],
        ),
        DemandManagement(
            date="2012-01-01",
            hour=6,
            temp_offsets=[0, 0, 20, 20, 0, 0, 0, 0, 0, -20, -20, -20],
        ),
    ],
)
```

A successful invocation of `issue_demand_managements()` returns an `EcobeeStatusResponse` instance.

## Runtime report job requests

### Create runtime report job

```python
from datetime import date

create_runtime_report_job_response = ecobee_service.create_runtime_report_job(
    selection=Selection(
        selection_type=SelectionType.THERMOSTATS, selection_match="123456789012"
    ),
    start_date=date(2016, 7, 1),
    end_date=date(2016, 10, 1),
    columns="zoneCalendarEvent,zoneHvacMode,zoneHeatTemp,zoneCoolTemp,zoneAveTemp,dmOffset",
)
logger.info(create_runtime_report_job_response.pretty_format())
assert create_runtime_report_job_response.status.code == 0, (
    f"Failure while executing create_runtime_report_job:\n{create_runtime_report_job_response.pretty_format()}"
)
```

A successful invocation of `create_runtime_report_job()` returns an `EcobeeCreateRuntimeReportJobResponse` instance.

### List runtime report job status

```python
list_runtime_report_job_status_response = ecobee_service.list_runtime_report_job_status(
    job_id="123"
)
```

A successful invocation of `list_runtime_report_job_status()` returns an
`EcobeeListRuntimeReportJobStatusResponse` instance.

### Cancel runtime report job

```python
cancel_runtime_report_job_response = ecobee_service.cancel_runtime_report_job(
    job_id="123"
)
```

A successful invocation of `cancel_runtime_report_job()` returns an `EcobeeStatusResponse` instance.

## Thermostat functions

A successful invocation of any thermostat function returns an `EcobeeStatusResponse` instance.

### Send message

```python
update_thermostat_response = ecobee_service.send_message("Hello World")
logger.info(update_thermostat_response.pretty_format())
assert update_thermostat_response.status.code == 0, (
    f"Failure while executing send_message:\n{update_thermostat_response.pretty_format()}"
)
```

### Acknowledge

```python
from pyecobee import AckType

selection = Selection(
    selection_type=SelectionType.REGISTERED,
    selection_match="",
    include_alerts=True,
)
thermostat_response = ecobee_service.request_thermostats(selection)
thermostat = thermostat_response.thermostat_list[0]
alerts = [alert for alert in thermostat.alerts if alert.text == message]

update_thermostat_response = ecobee_service.acknowledge(
    thermostat_identifier=thermostat.identifier,
    ack_ref=alerts[0].acknowledge_ref,
    ack_type=AckType.ACCEPT,
)
```

### Set hold

```python
from pyecobee import HoldType

# Simplest form
update_thermostat_response = ecobee_service.set_hold(
    hold_climate_ref="away",
    hold_type=HoldType.NEXT_TRANSITION,
)

# Using a specific start and end date and time
eastern = ZoneInfo("America/New_York")
update_thermostat_response = ecobee_service.set_hold(
    hold_climate_ref="away",
    start_date_time=datetime(2017, 5, 10, 13, 0, 0, tzinfo=eastern),
    end_date_time=datetime(2017, 5, 10, 14, 0, 0, tzinfo=eastern),
    hold_type=HoldType.DATE_TIME,
)

# Using a duration
update_thermostat_response = ecobee_service.set_hold(
    hold_climate_ref="away",
    start_date_time=datetime(2017, 5, 10, 13, 0, 0, tzinfo=eastern),
    hold_type=HoldType.HOLD_HOURS,
    hold_hours=1,
)

# A specific cooling temperature, held indefinitely
update_thermostat_response = ecobee_service.set_hold(
    cool_hold_temp=65,
    hold_type=HoldType.INDEFINITE,
)

# A specific heating temperature, held indefinitely
update_thermostat_response = ecobee_service.set_hold(
    heat_hold_temp=72,
    hold_type=HoldType.INDEFINITE,
)
```

### Resume program

```python
update_thermostat_response = ecobee_service.resume_program(resume_all=False)
```

### Create vacation

```python
from pyecobee import FanMode

eastern = ZoneInfo("America/New_York")
update_thermostat_response = ecobee_service.create_vacation(
    name="Christmas Vacation!",
    cool_hold_temp=104,
    heat_hold_temp=59,
    start_date_time=datetime(2017, 12, 23, 10, 0, 0, tzinfo=eastern),
    end_date_time=datetime(2017, 12, 28, 17, 0, 0, tzinfo=eastern),
    fan_mode=FanMode.AUTO,
    fan_min_on_time=0,
)
```

### Delete vacation

```python
update_thermostat_response = ecobee_service.delete_vacation(name="Christmas Vacation!")
```

### Reset preferences

```python
# Danger zone! This resets every user configurable setting to its factory default.
update_thermostat_response = ecobee_service.reset_preferences()
```

## Credentials

The ecobee API requires that every credential it issues is stored by the application, and it replaces the refresh
token each time it issues one. Pyecobee therefore takes the credentials you hold and a callback to store the ones it
receives.

`JsonFileTokenStore` writes the credentials as JSON in a file only your user can read, which is all most applications
need. Its `load` and `save` are the two arguments the service asks for.

```python
from pyecobee import EcobeeService, JsonFileTokenStore

store = JsonFileTokenStore("~/.config/pyecobee/tokens.json")
ecobee_service = EcobeeService(
    "My Thermostat",
    application_key,
    store.load(),
    store.save,
)
```

The file is written under a temporary name and renamed into place, so an interrupted save cannot leave a half-written
file where your credentials used to be.

Anywhere else you want to keep them, supply your own pair. `Tokens` is an immutable snapshot that converts to and from
a plain mapping through `to_dict` and `from_dict`, so a store is usually a few lines. For a desktop application,
consider [keyring](https://pypi.org/project/keyring/). For a server, take the application key and the initial
credentials from the environment or a secret manager.

`Tokens` omits the credentials from its representation, so logging one discloses only the expiries and the scope:

```pycon
>>> ecobee_service.tokens
Tokens(held=access_token, refresh_token, access_token_expires_on=..., refresh_token_expires_on=..., scope=<Scope.SMART_WRITE: 'smartWrite'>)
```

### First run

Authorization is only needed when no credentials are held. The callback stores whatever each step produces.

```python
if ecobee_service.authorization_token is None:
    authorize_response = ecobee_service.authorize()
    logger.info(
        "Go to ecobee.com, log in to the web portal and click on the settings tab. Ensure the My Apps widget is "
        "enabled. If it is not, click on the My Apps option in the menu on the left. In the My Apps widget paste "
        f'"{authorize_response.ecobee_pin}" in the textbox labelled "Enter your 4 digit pin to install your third '
        'party app" and then click "Install App". The next screen will display any permissions the app requires '
        'and will ask you to click "Authorize" to add the application.'
    )
    input("Press Enter once the app is authorized...")

if ecobee_service.access_token is None:
    ecobee_service.request_tokens()
```

## Token renewal

An access token expires 3599 seconds (1 hour) after it is issued. A refresh token expires 30 days after it is
issued, and the ecobee API does not report that expiry, so Pyecobee derives it.

Renewal is automatic. Before each request Pyecobee renews an access token that is within two minutes of expiring,
and if ecobee answers that the token has already expired, it renews the credentials and sends the request once more.
Each renewal reaches your callback.

```python
# No token handling required. The request renews the credentials if it has to.
thermostat_summary_response = ecobee_service.request_thermostats_summary(
    selection=Selection(
        selection_type=SelectionType.REGISTERED,
        selection_match="",
        include_equipment_status=True,
    )
)
```

Renewal needs a refresh token that is still valid. Once one has expired, ecobee raises
`EcobeeAuthorizationException` and the application must authorize again:

```python
from pyecobee import EcobeeAuthorizationException

try:
    thermostat_response = ecobee_service.request_thermostats(selection)
except EcobeeAuthorizationException:
    authorize_again(ecobee_service)
```

`refresh_tokens()` remains available for an application that would rather renew on its own schedule, such as before
a long idle period.

## Date and time handling

Some ecobee API requests expect a date and time in thermostat time, while others expect UTC.

Every `EcobeeService` method that accepts a `datetime` expects it in thermostat time, and the `datetime` **must be
timezone aware**.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

eastern = ZoneInfo("America/New_York")
start_date_time = datetime(
    2017, 5, 1, 10, 0, 0, tzinfo=eastern
)  # 2017/05/01 10:00:00 -0400
```

The method then either uses the `datetime` as is, or converts it to UTC, depending on what the ecobee API request
requires.

## Exception handling

Your code should be prepared to handle the following exceptions:

- `EcobeeApiException`: raised if a request results in an ecobee API error response. Exposes `status_code` and
  `status_message`.
- `EcobeeAuthorizationException`: raised if a request results in a standard or extended OAuth error response.
  Exposes `error`, `error_description` and `error_uri`.
- `EcobeeRequestsException`: raised if a request results in an exception from the underlying `requests` module.
- `EcobeeHttpException`: raised if a request results in any other HTTP error.
- `EcobeeDeserializationException`: raised if a response cannot be converted into a model.

All of them derive from `EcobeeException`.

## Development

Pyecobee is developed with [uv](https://docs.astral.sh/uv/) and [Ruff](https://docs.astral.sh/ruff/). To create the
locked development environment:

```bash
uv sync --locked
```

Run the lint and formatting checks:

```bash
uv run ruff check .
uv run ruff format --check .
```

Run the offline regression suite, which enforces a 60% coverage minimum:

```bash
uv run pytest
```

Apply safe lint fixes, sort imports, and format the source tree:

```bash
uv run ruff check . --select I --fix
uv run ruff check . --fix
uv run ruff format .
```

See [`CHANGELOG.md`](CHANGELOG.md) for release notes and [`MIGRATION.md`](MIGRATION.md) for the 1.x to 2.0 upgrade
path.

## License

[MIT](LICENSE)
