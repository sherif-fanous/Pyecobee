import logging.handlers
import shelve
import sys
import traceback
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from pyecobee import *

logger = logging.getLogger(__name__)


class MultiLineFormatter(logging.Formatter):
    def format(self, record):
        formatted_string = logging.Formatter.format(self, record)
        header, _ = formatted_string.split(record.message)
        formatted_string = formatted_string.replace("\n", "\n" + " " * len(header))
        return formatted_string


def test_update_groups(ecobee_service, groups):
    logger.info("Updating Groups")
    selection = Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match=""
    )
    group_response = ecobee_service.update_groups(selection, groups)
    validate_dictionary_to_object(group_response)
    assert group_response.status.code == 0, (
        f"Failure while executing update_groups:\n{group_response.pretty_format()}"
    )

    return group_response.groups


def test_request_groups(ecobee_service):
    logger.info("Requesting Groups")
    selection = Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match=""
    )
    group_response = ecobee_service.request_groups(selection)
    validate_dictionary_to_object(group_response)
    assert group_response.status.code == 0, (
        f"Failure while executing request_groups:\n{group_response.pretty_format()}"
    )

    return group_response.groups


def test_runtime_reports(ecobee_service, thermostat):
    eastern = ZoneInfo("America/New_York")

    logger.info("Requesting Runtime Report")
    selection = Selection(
        selection_type=SelectionType.THERMOSTATS.value,
        selection_match=thermostat.identifier,
    )
    runtime_reports_response = ecobee_service.request_runtime_reports(
        selection,
        start_date_time=datetime(2017, 5, 1, 0, 0, 0).replace(tzinfo=eastern),
        end_date_time=datetime(2017, 5, 2, 0, 0, 0).replace(tzinfo=eastern),
        columns="auxHeat1,auxHeat2,auxHeat3,compCool1,"
        "compCool2,compHeat1,compHeat2,"
        "dehumidifier,dmOffset,economizer,"
        "fan,humidifier,hvacMode,"
        "outdoorHumidity,outdoorTemp,sky,"
        "ventilator,wind,zoneAveTemp,"
        "zoneCalendarEvent,zoneClimate,"
        "zoneCoolTemp,zoneHeatTemp,"
        "zoneHumidity,zoneHumidityHigh,"
        "zoneHumidityLow,zoneHvacMode,"
        "zoneOccupancy",
    )
    validate_dictionary_to_object(runtime_reports_response)
    assert runtime_reports_response.status.code == 0, (
        f"Failure while executing request_runtime_reports:\n{runtime_reports_response.pretty_format()}"
    )


def test_request_meter_reports(ecobee_service, thermostat):
    eastern = ZoneInfo("America/New_York")

    logger.info("Requesting Meter Report")
    selection = Selection(
        selection_type=SelectionType.THERMOSTATS.value,
        selection_match=thermostat.identifier,
    )
    meter_reports_response = ecobee_service.request_meter_reports(
        selection,
        start_date_time=datetime(2017, 4, 1, 0, 0, 0).replace(tzinfo=eastern),
        end_date_time=datetime(2017, 4, 2, 0, 0, 0).replace(tzinfo=eastern),
    )
    validate_dictionary_to_object(meter_reports_response)
    assert meter_reports_response.status.code == 0, (
        f"Failure while executing request_meter_reports:\n{meter_reports_response.pretty_format()}"
    )


def test_update_thermosats(ecobee_service, fan_min_on_time):
    logger.info("Updating Thermostats")
    selection = Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match=""
    )
    settings = Settings(fan_min_on_time=fan_min_on_time)
    thermostat = Thermostat(identifier="250891030972", settings=settings)
    update_thermostats_response = ecobee_service.update_thermostats(
        selection, thermostat
    )
    validate_dictionary_to_object(update_thermostats_response)
    assert update_thermostats_response.status.code == 0, (
        f"Failure while executing update_thermostats:\n{update_thermostats_response.pretty_format()}"
    )


def test_request_thermostats_summary(ecobee_service):
    logger.info("Requesting Thermostat Summary")
    selection = Selection(
        selection_type=SelectionType.REGISTERED.value,
        selection_match="",
        include_equipment_status=False,
    )
    thermostats_summary_response = ecobee_service.request_thermostats_summary(selection)
    validate_dictionary_to_object(thermostats_summary_response)
    assert thermostats_summary_response.status.code == 0, (
        f"Failure while executing request_thermostats_summary:\n{thermostats_summary_response.pretty_format()}"
    )
    logger.info(thermostats_summary_response.pretty_format())


def test_request_thermostats_all(ecobee_service):
    logger.info("Requesting Thermostats (All Data)")
    selection = Selection(
        selection_type=SelectionType.REGISTERED.value,
        selection_match="",
        include_alerts=False,
        include_audio=False,
        include_energy=False,
        include_device=False,
        include_electricity=False,
        include_equipment_status=True,
        include_events=True,
        include_extended_runtime=False,
        include_house_details=False,
        include_location=False,
        include_management=False,
        include_notification_settings=False,
        include_oem_cfg=False,
        include_privacy=False,
        include_program=False,
        include_reminders=True,
        include_runtime=True,
        include_security_settings=False,
        include_sensors=True,
        include_settings=True,
        include_technician=False,
        include_utility=False,
        include_version=False,
        include_weather=False,
    )
    thermostats_response = ecobee_service.request_thermostats(selection)
    validate_dictionary_to_object(thermostats_response)
    assert thermostats_response.status.code == 0, (
        f"Failure while executing request_thermostats:\n{thermostats_response.pretty_format()}"
    )
    logger.info("%s", thermostats_response.pretty_format())

    return thermostats_response.thermostat_list[0]


def test_request_thermostats_minimal(ecobee_service):
    logger.info("Requesting Thermostats (Minimal Data)")
    selection = Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match=""
    )
    thermostats_response = ecobee_service.request_thermostats(selection)
    validate_dictionary_to_object(thermostats_response)
    assert thermostats_response.status.code == 0, (
        f"Failure while executing request_thermostats:\n{thermostats_response.pretty_format()}"
    )

    return thermostats_response.thermostat_list[0]


def test_resume_program(ecobee_service):
    logger.info("Resuming Program")
    update_thermostat_response = ecobee_service.resume_program(resume_all=False)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, (
        f"Failure while executing resume_program:\n{update_thermostat_response.pretty_format()}"
    )


def test_set_hold(ecobee_service):
    logger.info("Setting Hold")
    update_thermostat_response = ecobee_service.set_hold(
        hold_climate_ref="away", hold_type=HoldType.NEXT_TRANSITION
    )
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, (
        f"Failure while executing set_hold:\n{update_thermostat_response.pretty_format()}"
    )


def test_acknowledge(ecobee_service, thermostat, alert):
    logger.info("Acknowledging Alert: %s", alert.text)
    update_thermostat_response = ecobee_service.acknowledge(
        thermostat_identifier=thermostat.identifier,
        ack_ref=alert.acknowledge_ref,
        ack_type=AckType.ACCEPT,
    )
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, (
        f"Failure while executing acknowledge:\n{update_thermostat_response.pretty_format()}"
    )


def test_send_message(ecobee_service, message):
    logger.info("Sending Message: %s", message)
    update_thermostat_response = ecobee_service.send_message(message)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, (
        f"Failure while executing send_message:\n{update_thermostat_response.pretty_format()}"
    )


def test_delete_vacation(ecobee_service, vacation_name):
    logger.info("Deleting Vacation: %s", vacation_name)
    update_thermostat_response = ecobee_service.delete_vacation(name=vacation_name)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, (
        f"Failure while executing delete_vacation:\n{update_thermostat_response.pretty_format()}"
    )


def test_create_vacation(ecobee_service, vacation_name):
    eastern = ZoneInfo("America/New_York")

    logger.info("Creating Vacation: %s", vacation_name)
    update_thermostat_response = ecobee_service.create_vacation(
        name=vacation_name,
        cool_hold_temp=104,
        heat_hold_temp=59,
        start_date_time=datetime(2017, 12, 23, 10, 0, 0).replace(tzinfo=eastern),
        end_date_time=datetime(2018, 1, 9, 4, 0, 0).replace(tzinfo=eastern),
        fan_mode=FanMode.AUTO,
        fan_min_on_time=0,
    )
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, (
        f"Failure while executing create_vacation:\n{update_thermostat_response.pretty_format()}"
    )


def validate_dictionary_to_object(object_, parents=[], expected_type_of_object=None):
    if hasattr(object_, "__slots__"):
        parents.append(object_.__class__.__name__)
        for attribute_name in object_.__slots__:
            parents.append(attribute_name)
            attribute_value = getattr(object_, attribute_name)
            if attribute_value is not None:
                attribute_value_actual_type = type(attribute_value).__name__
                attribute_value_expected_type = type(object_).attribute_type_map[
                    attribute_name[1:]
                ]
                attribute_value_expected_type = (
                    eval(type(object_).attribute_type_map[attribute_name[1:]]).__name__
                    if attribute_value_expected_type.find("List") == -1
                    else "list"
                )

                assert attribute_value_actual_type == attribute_value_expected_type, (
                    "{}{}. Type of {} is {} , expected {}".format(
                        ".".join(parents),
                        object_.__class__.__name__,
                        attribute_name,
                        attribute_value_actual_type,
                        attribute_value_expected_type,
                    )
                )

                if isinstance(attribute_value, list):
                    for list_entry in attribute_value:
                        validate_dictionary_to_object(
                            list_entry,
                            parents,
                            eval(
                                type(object_).attribute_type_map[attribute_name[1:]][
                                    5:-1
                                ]
                            ).__name__,
                        )
                else:
                    validate_dictionary_to_object(
                        attribute_value, parents, attribute_value_expected_type
                    )
            parents.pop()
        parents.pop()
    elif isinstance(object_, list):
        for list_entry in object_:
            validate_dictionary_to_object(list_entry, parents, expected_type_of_object)
    else:
        assert type(object_).__name__ == expected_type_of_object, (
            "{}. Type of {} is {}, expected {}".format(
                ".".join(parents),
                object_,
                type(object_).__name__,
                expected_type_of_object,
            )
        )


def fahrenheit_to_celsius(temperature):
    return (temperature - 32) / 1.8


def celsius_to_fahrenheit(temperature):
    return (temperature * 1.8) + 32


def persist_to_shelf(file_name, ecobee_service):
    pyecobee_db = shelve.open(file_name, protocol=2)
    pyecobee_db[ecobee_service.thermostat_name] = ecobee_service
    pyecobee_db.close()


def refresh_tokens(ecobee_service):
    logger.info("Refreshing Tokens")
    ecobee_service.refresh_tokens()
    persist_to_shelf("pyecobee_db", ecobee_service)


def request_tokens(ecobee_service):
    logger.info("Requesting Tokens")
    ecobee_service.request_tokens()
    persist_to_shelf("pyecobee_db", ecobee_service)


def authorize(ecobee_service):
    logger.info("Authorizing App")
    authorize_response = ecobee_service.authorize()
    persist_to_shelf("pyecobee_db", ecobee_service)

    logger.info(
        "Please goto ecobee.com, login to the web portal and click on the "
        "settings tab. Ensure the My Apps widget is enabled. If it is not "
        "click on the My Apps option in the menu on the left. In the My Apps "
        'widget paste "%s" and in the textbox labelled "Enter your 4 digit '
        'pin to install your third party app" and then click "Install App". '
        "The next screen will display any permissions the app requires and "
        'will ask you to click "Authorize" to add the application.\n\n'
        'After completing this step please hit "Enter" to continue.',
        authorize_response.ecobee_pin,
    )
    input()


def main():
    try:
        python_version = sys.version_info

        rotating_file_handler = logging.handlers.RotatingFileHandler(
            f"pyecobee_log_{python_version[0]}.{python_version[1]}.txt",
            maxBytes=1048576,
            backupCount=10,
        )
        stream_handler = logging.StreamHandler()

        formatter = MultiLineFormatter(
            "%(asctime)s %(name)-18s %(levelname)-8s %(message)s"
        )

        rotating_file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(rotating_file_handler)
        logger.addHandler(stream_handler)

        logger.setLevel(logging.DEBUG)

        logging.getLogger("pyecobee").setLevel(logging.DEBUG)
        logging.getLogger("pyecobee").addHandler(rotating_file_handler)
        logging.getLogger("pyecobee").addHandler(stream_handler)

        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        thermostat_name = (
            f"ecobeeThermostat@Home_{python_version[0]}.{python_version[1]}"
        )
        pyecobee_db = None
        try:
            pyecobee_db = shelve.open("pyecobee_db", protocol=2)
            ecobee_service = pyecobee_db[thermostat_name]
        except KeyError:
            application_key = input("Please enter the API key of your ecobee App: ")
            ecobee_service = EcobeeService(
                thermostat_name=thermostat_name, application_key=application_key
            )
        finally:
            if pyecobee_db is not None:
                pyecobee_db.close()

        if not ecobee_service.authorization_token:
            authorize(ecobee_service)
        if not ecobee_service.access_token:
            request_tokens(ecobee_service)

        now_utc = datetime.now(UTC)
        if now_utc > ecobee_service.refresh_token_expires_on:
            authorize(ecobee_service)
            request_tokens(ecobee_service)
        elif now_utc > ecobee_service.access_token_expires_on:
            refresh_tokens(ecobee_service)

        logger.debug(ecobee_service.pretty_format())

        # logger.info(
        #     'Access Token             => {0}\n'
        #     'Access Token Expires On  => {1}\n'
        #     'Refresh Token            => {2}\n'
        #     'Refresh Token Expires On => {3}'.format(
        #         ecobee_service.access_token,
        #         ecobee_service.access_token_expires_on,
        #         ecobee_service.refresh_token,
        #         ecobee_service.refresh_token_expires_on))

        # Remove Hierarchy Users
        # ecobee_service.remove_hierarchy_users(
        #     set_path='/',
        #     users=[
        #         HierarchyUser(
        #             user_name='todelete@hierarchy.com'
        #         ),
        #         HierarchyUser(
        #             user_name='todelete2@hierarchy.com'
        #         )])
        # logger.info(remove_hierarchy_users_response.pretty_format())
        # assert remove_hierarchy_users_response.status.code == 0, (
        #     'Failure while executing remove_hierarchy_users:\n{0}'.format(
        #         remove_hierarchy_users_response.pretty_format()))

        # Unregister Hierarchy Users
        # ecobee_service.unregister_hierarchy_users(
        #     users=[
        #         HierarchyUser(
        #             user_name='todelete@hierarchy.com'),
        #         HierarchyUser(
        #             user_name='todelete2@hierarchy.com')])

        # Update Hierarchy Users
        # ecobee_service.update_hierarchy_users(
        #     users=[HierarchyUser(
        #         user_name='user1@update.com',
        #         first_name='Updated',
        #         last_name='User',
        #         phone='222-333-4444',
        #         email_alerts=False)
        #     ], privileges=[
        #         HierarchyPrivilege(set_path='/MainNode',
        #                            user_name='user1@update.com',
        #                            allow_view=False),
        #         HierarchyPrivilege(set_path='/MainNode',
        #                            user_name='user2@update.com',
        #                            allow_view=False),
        #         HierarchyPrivilege(set_path='/OtherNode',
        #                            user_name='user2@update.com',
        #                            allow_view=False)])

        # Register Hierarchy Thermostat
        # ecobee_service.register_hierarchy_thermostats(
        #     set_path='/OtherNode',
        #     thermostats=(
        #         '123456789012,'
        #         '123456789013'))

        # Unregister Hierarchy Thermostat
        # ecobee_service.unregister_hierarchy_thermostats(
        #     thermostats='123456789012,123456789013')

        # Move Hierarchy Thermostat
        # ecobee_service.move_hierarchy_thermostats(set_path='/MainNode',
        #                                           to_path='/OtherNode',
        #                                           thermostats=('123456789012,'
        #                                                        '123456789013'))

        # Assign Hierarchy Thermostat
        # ecobee_service.assign_hierarchy_thermostats(
        # set_path='/MainNode', thermostats=('123456789012,' '123456789013'))

        # List Demand EcobeeResponse
        # ecobee_service.list_demand_responses()

        # Issue Demand EcobeeResponse
        # ecobee_service.issue_demand_response(
        #     selection=Selection(
        #         selection_type=SelectionType.MANAGEMENT_SET.value,
        #         selection_match='/'),
        #     demand_response=DemandResponse(
        #         name='myDR',
        #         message='This is a DR!',
        #         event=Event(
        #             heat_hold_temp=790,
        #             end_time='11:37:18',
        #             end_date='2011-01-10',
        #             name='apiDR',
        #             type='useEndTime',
        #             cool_hold_temp=790,
        #             start_date='2011-01-09',
        #             start_time='11:37:18',
        #             is_temperature_absolute=False)))

        # Cancel Demand EcobeeResponse
        # ecobee_service.cancel_demand_response(
        #     demand_response_ref='c253a12e0b3c3c93800095')

        # Issue Demand Management
        # ecobee_service.issue_demand_managements(
        #     selection=Selection(
        #         selection_type=SelectionType.MANAGEMENT_SET.value,
        #         selection_match='/'),
        #     demand_managements=[
        #         DemandManagement(
        #             date='2012-01-01',
        #             hour=5,
        #             temp_offsets=[20, 20, 20, 0, 0, 0, 0, -20, -20, -20, 0, 0]),
        #         DemandManagement(
        #             date='2012-01-01',
        #             hour=6,
        # temp_offsets=[0, 0, 20, 20, 0, 0, 0, 0, 0, -20, -20, -20])])

        # Create Runtime Report Job
        # ecobee_service.create_runtime_report_job(
        #     selection=Selection(
        #         selection_type=SelectionType.THERMOSTATS.value,
        #         selection_match='123456789012',
        #     ),
        #     start_date=date(2016, 7, 1),
        #     end_date=date(2016, 10, 1),
        #     columns='zoneCalendarEvent,zoneHvacMode,zoneHeatTemp,zoneCoolTemp,zoneAveTemp,dmOffset',
        # )

        # List Runtime Report Job Status
        # ecobee_service.list_runtime_report_job_status(job_id='123')

        # Cancel Runtime Report Job
        # ecobee_service.cancel_runtime_report_job(job_id='123')

        # class_ = EcobeeListRuntimeReportJobStatusResponse
        # response = dictionary_to_object(
        #     {class_.__name__: json.loads(open('list_runtime_report_job_response.txt').read())},
        #     {class_.__name__: class_},
        #     {class_.__name__: None},
        #     is_top_level=False)
        # logger.info(response.pretty_format())
        # sys.exit(0)

        # Create Vacation
        # vacation_name = 'Vacation_{0}.{1}'.format(
        #     python_version[0], python_version[1])
        # test_create_vacation(ecobee_service, vacation_name)

        # Send Message
        # message = 'Hello Pyecobee_{0}.{1}'.format(
        #     python_version[0], python_version[1])
        # test_send_message(ecobee_service, message)

        # Set Hold
        # test_set_hold(ecobee_service)

        # input('Check hold')

        # Update Thermostat
        # fan_min_on_time = 15
        # test_update_thermosats(ecobee_service, fan_min_on_time)

        # Get Thermostats
        thermostat = test_request_thermostats_all(ecobee_service)

        # events = [event for event in thermostat.events
        #           if event.name == vacation_name]
        # assert events, 'Failure while asserting create_vacation'

        # alerts = [alert for alert in thermostat.alerts
        #           if alert.text == message]
        # assert alerts, 'Failure while asserting send_message.'

        # assert thermostat.settings.fan_min_on_time == fan_min_on_time, \
        #     'Failure while asserting update_thermostats'

        # Delete Vacation
        # test_delete_vacation(ecobee_service, vacation_name)

        # Acknowledge
        # test_acknowledge(ecobee_service, thermostat, alerts[0])

        # Resume Program
        # test_resume_program(ecobee_service)

        # thermostat = test_request_thermostats_all(ecobee_service)

        # events = [event for event in thermostat.events
        #           if event.name == vacation_name]
        # assert not events, 'Failure while asserting delete_vacation'

        # alerts = [alert for alert in thermostat.alerts
        #           if alert.text == message]
        # assert not alerts, 'Failure while asserting acknowledge.'

        # Thermostat Summary
        # test_request_thermostats_summary(ecobee_service)

        # Meter Reports
        # test_request_meter_reports(ecobee_service, thermostat)

        # Runtime Reports
        # test_runtime_reports(ecobee_service, thermostat)

        # Update Groups
        # groups = [
        #     Group(
        #         group_name='Group_{0}.{1}'.format(
        #             python_version[0],
        #             python_version[1]),
        #         synchronize_alerts=False,
        #         synchronize_vacation=False,
        #         thermostats=[
        #             thermostat.identifier])]
        # groups = test_update_groups(ecobee_service, groups)

        # groups = [
        #     Group(
        #         group_name='Group_{0}.{1}'.format(
        #             python_version[0],
        #             python_version[1]),
        #         group_ref=groups[0].group_ref)]
        # groups = test_update_groups(ecobee_service, groups)
        # groups = test_request_groups(ecobee_service)

        logger.info("All tests passed!!!")
    except EcobeeException:
        logger.exception(traceback.format_exc())


if __name__ == "__main__":
    main()
