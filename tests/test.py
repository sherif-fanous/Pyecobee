import logging.handlers
import shelve
import sys
import traceback
from datetime import datetime

import six
import pytz
from pytz import timezone
from six.moves import input

from pyecobee import *

logger = logging.getLogger(__name__)


class MultiLineFormatter(logging.Formatter):
    def format(self, record):
        formatted_string = logging.Formatter.format(self, record)
        header, footer = formatted_string.split(record.message)
        formatted_string = formatted_string.replace('\n', '\n' + ' ' * len(header))
        return formatted_string


def test_update_groups(ecobee_service, groups):
    logger.info('Updating Groups')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='')
    group_response = ecobee_service.update_groups(selection, groups)
    validate_dictionary_to_object(group_response)
    assert group_response.status.code == 0, 'Failure while executing update_groups:\n{0}'.format(
        group_response.pretty_format())

    return group_response.groups


def test_request_groups(ecobee_service):
    logger.info('Requesting Groups')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='')
    group_response = ecobee_service.request_groups(selection)
    validate_dictionary_to_object(group_response)
    assert group_response.status.code == 0, 'Failure while executing request_groups:\n{0}'.format(
        group_response.pretty_format())

    return group_response.groups


def test_runtime_reports(ecobee_service, thermostat):
    eastern = timezone('US/Eastern')

    logger.info('Requesting Runtime Report')
    selection = Selection(selection_type=SelectionType.THERMOSTATS.value, selection_match=thermostat.identifier)
    runtime_reports_response = ecobee_service.request_runtime_reports(selection,
                                                                      start_date_time=eastern.localize(datetime(
                                                                          2017, 5, 1, 0, 0, 0),
                                                                          is_dst=True),
                                                                      end_date_time=eastern.localize(datetime(
                                                                          2017, 5, 2, 0, 0, 0),
                                                                          is_dst=True),
                                                                      columns='auxHeat1,auxHeat2,auxHeat3,compCool1,'
                                                                              'compCool2,compHeat1,compHeat2,'
                                                                              'dehumidifier,dmOffset,economizer,'
                                                                              'fan,humidifier,hvacMode,'
                                                                              'outdoorHumidity,outdoorTemp,sky,'
                                                                              'ventilator,wind,zoneAveTemp,'
                                                                              'zoneCalendarEvent,zoneClimate,'
                                                                              'zoneCoolTemp,zoneHeatTemp,'
                                                                              'zoneHumidity,zoneHumidityHigh,'
                                                                              'zoneHumidityLow,zoneHvacMode,'
                                                                              'zoneOccupancy')
    validate_dictionary_to_object(runtime_reports_response)
    assert runtime_reports_response.status.code == 0, 'Failure while executing request_runtime_reports:\n{0}'.format(
        runtime_reports_response.pretty_format())


def test_request_meter_reports(ecobee_service, thermostat):
    eastern = timezone('US/Eastern')

    logger.info('Requesting Meter Report')
    selection = Selection(selection_type=SelectionType.THERMOSTATS.value, selection_match=thermostat.identifier)
    meter_reports_response = ecobee_service.request_meter_reports(selection,
                                                                  start_date_time=eastern.localize(datetime(
                                                                      2017, 4, 1, 0, 0, 0),
                                                                      is_dst=True),
                                                                  end_date_time=eastern.localize(datetime(
                                                                      2017, 4, 2, 0, 0, 0),
                                                                      is_dst=True))
    validate_dictionary_to_object(meter_reports_response)
    assert meter_reports_response.status.code == 0, 'Failure while executing request_meter_reports:\n{0}'.format(
        meter_reports_response.pretty_format())


def test_update_thermosats(ecobee_service, fan_min_on_time):
    logger.info('Updating Thermostats')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='')
    settings = Settings(fan_min_on_time=fan_min_on_time)
    thermostat = Thermostat(identifier='250891030972', settings=settings)
    update_thermostats_response = ecobee_service.update_thermostats(selection, thermostat)
    validate_dictionary_to_object(update_thermostats_response)
    assert update_thermostats_response.status.code == 0, 'Failure while executing update_thermostats:\n{0}'.format(
        update_thermostats_response.pretty_format())


def test_request_thermostats_summary(ecobee_service):
    logger.info('Requesting Thermostat Summary')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='',
                          include_equipment_status=True)
    thermostats_summary_response = ecobee_service.request_thermostats_summary(selection)
    validate_dictionary_to_object(thermostats_summary_response)
    assert thermostats_summary_response.status.code == 0, \
        'Failure while executing request_thermostats_summary:\n{0}'.format(
            thermostats_summary_response.pretty_format())
    logger.info(thermostats_summary_response.pretty_format())


def test_request_thermostats_all(ecobee_service):
    logger.info('Requesting Thermostats (All Data)')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='', include_alerts=True,
                          include_audio=True, include_energy=True,
                          include_device=True, include_electricity=True, include_equipment_status=True,
                          include_events=True, include_extended_runtime=True, include_house_details=True,
                          include_location=True, include_management=True, include_notification_settings=True,
                          include_oem_cfg=False, include_privacy=False, include_program=True, include_reminders=True,
                          include_runtime=True, include_security_settings=False, include_sensors=True,
                          include_settings=True, include_technician=True, include_utility=True, include_version=True,
                          include_weather=True)
    thermostats_response = ecobee_service.request_thermostats(selection)
    validate_dictionary_to_object(thermostats_response)
    assert thermostats_response.status.code == 0, 'Failure while executing request_thermostats:\n{0}'.format(
        thermostats_response.pretty_format())
    logger.info('{0}'.format(thermostats_response.pretty_format()))

    return thermostats_response.thermostat_list[0]


def test_request_thermostats_minimal(ecobee_service):
    logger.info('Requesting Thermostats (Minimal Data)')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='')
    thermostats_response = ecobee_service.request_thermostats(selection)
    validate_dictionary_to_object(thermostats_response)
    assert thermostats_response.status.code == 0, 'Failure while executing request_thermostats:\n{0}'.format(
        thermostats_response.pretty_format())

    return thermostats_response.thermostat_list[0]


def test_resume_program(ecobee_service):
    logger.info('Resuming Program')
    update_thermostat_response = ecobee_service.resume_program(resume_all=False)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, 'Failure while executing resume_program:\n{0}'.format(
        update_thermostat_response.pretty_format())


def test_set_hold(ecobee_service):
    logger.info('Setting Hold')
    update_thermostat_response = ecobee_service.set_hold(hold_climate_ref='away', hold_type=HoldType.NEXT_TRANSITION)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, 'Failure while executing set_hold:\n{0}'.format(
        update_thermostat_response.pretty_format())


def test_acknowledge(ecobee_service, thermostat, alert):
    logger.info('Acknowledging Alert: {0}'.format(alert.text))
    update_thermostat_response = ecobee_service.acknowledge(thermostat_identifier=thermostat.identifier,
                                                            ack_ref=alert.acknowledge_ref,
                                                            ack_type=AckType.ACCEPT)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, 'Failure while executing acknowledge:\n{0}'.format(
        update_thermostat_response.pretty_format())


def test_send_message(ecobee_service, message):
    logger.info('Sending Message: {0}'.format(message))
    update_thermostat_response = ecobee_service.send_message(message)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, 'Failure while executing send_message:\n{0}'.format(
        update_thermostat_response.pretty_format())


def test_delete_vacation(ecobee_service, vacation_name):
    logger.info('Deleting Vacation: {0}'.format(vacation_name))
    update_thermostat_response = ecobee_service.delete_vacation(name=vacation_name)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, 'Failure while executing delete_vacation:\n{0}'.format(
        update_thermostat_response.pretty_format())


def test_create_vacation(ecobee_service, vacation_name):
    eastern = timezone('US/Eastern')

    logger.info('Creating Vacation: {0}'.format(vacation_name))
    update_thermostat_response = ecobee_service.create_vacation(name=vacation_name,
                                                                cool_hold_temp=104,
                                                                heat_hold_temp=59,
                                                                start_date_time=eastern.localize(datetime(2017, 12, 23,
                                                                                                          10, 0, 0),
                                                                                                 is_dst=False),
                                                                end_date_time=eastern.localize(datetime(2018, 1, 9,
                                                                                                        4, 0, 0),
                                                                                               is_dst=False),
                                                                fan_mode=FanMode.AUTO,
                                                                fan_min_on_time=0)
    validate_dictionary_to_object(update_thermostat_response)
    assert update_thermostat_response.status.code == 0, 'Failure while executing create_vacation:\n{0}'.format(
        update_thermostat_response.pretty_format())


def validate_dictionary_to_object(object_, parents=[], expected_type_of_object=None):
    if hasattr(object_, '__slots__'):
        parents.append(object_.__class__.__name__)
        for attribute_name in object_.__slots__:
            parents.append(attribute_name)
            attribute_value = getattr(object_, attribute_name)
            if attribute_value is not None:
                attribute_value_actual_type = type(attribute_value).__name__
                attribute_value_expected_type = type(object_).attribute_type_map[attribute_name[1:]]
                attribute_value_expected_type = eval(type(object_).attribute_type_map[attribute_name[1:]]).__name__ \
                    if attribute_value_expected_type.find('List') == -1 else 'list'

                assert attribute_value_actual_type == attribute_value_expected_type, \
                    '{0}{1}. Type of {2} is {3} , expected {4}'.format('.'.join(parents),
                                                                       object_.__class__.__name__,
                                                                       attribute_name,
                                                                       attribute_value_actual_type,
                                                                       attribute_value_expected_type)

                if isinstance(attribute_value, list):
                    for list_entry in attribute_value:
                        validate_dictionary_to_object(list_entry,
                                                      parents,
                                                      eval(type(object_).attribute_type_map[attribute_name[1:]][
                                                           5:-1]).__name__)
                else:
                    validate_dictionary_to_object(attribute_value, parents, attribute_value_expected_type)
            parents.pop()
        parents.pop()
    elif isinstance(object_, list):
        for list_entry in object_:
            validate_dictionary_to_object(list_entry, parents, expected_type_of_object)
    else:
        assert type(object_).__name__ == expected_type_of_object, \
            '{0}. Type of {1} is {2}, expected {3}'.format('.'.join(parents), object_, type(object_).__name__,
                                                           expected_type_of_object)


def fahrenheit_to_celsius(temperature):
    return (temperature - 32) / 1.8


def celsius_to_fahrenheit(temperature):
    return (temperature * 1.8) + 32


def persist_to_shelf(file_name, ecobee_service):
    pyecobee_db = shelve.open(file_name, protocol=2)
    pyecobee_db[ecobee_service.thermostat_name] = ecobee_service
    pyecobee_db.close()


def refresh_tokens(ecobee_service):
    logger.info('Refreshing Tokens')
    ecobee_service.refresh_tokens()
    persist_to_shelf('pyecobee_db', ecobee_service)


def request_tokens(ecobee_service):
    logger.info('Requesting Tokens')
    ecobee_service.request_tokens()
    persist_to_shelf('pyecobee_db', ecobee_service)


def authorize(ecobee_service):
    logger.info('Authorizing App')
    authorize_response = ecobee_service.authorize()
    persist_to_shelf('pyecobee_db', ecobee_service)

    logger.info('Please goto ecobee.com, login to the web portal and click on the settings tab. Ensure the My '
                'Apps widget is enabled. If it is not click on the My Apps option in the menu on the left. In the '
                'My Apps widget paste "{0}" and in the textbox labelled "Enter your 4 digit pin to '
                'install your third party app" and then click "Install App". The next screen will display any '
                'permissions the app requires and will ask you to click "Authorize" to add the application.\n'
                '\n'
                'After completing this step please hit "Enter" to continue.'.format(authorize_response.ecobee_pin))
    input()


def main():
    try:
        python_version = sys.version_info

        rotating_file_handler = logging.handlers.RotatingFileHandler(
            'pyecobee_log_{0}.{1}.txt'.format(
                python_version[0],
                python_version[1]),
            maxBytes=1048576,
            backupCount=10)
        stream_handler = logging.StreamHandler()
        formatter = MultiLineFormatter('%(asctime)s %(name)-18s %(levelname)-8s %(message)s')
        rotating_file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(rotating_file_handler)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        thermostat_name = 'ecobeeThermostat@Home_{0}.{1}'.format(python_version[0], python_version[1])
        pyecobee_db = None
        try:
            pyecobee_db = shelve.open('pyecobee_db', protocol=2)
            ecobee_service = pyecobee_db[thermostat_name]
        except KeyError:
            application_key = input('Please enter the API key of your ecobee App: ')
            ecobee_service = EcobeeService(thermostat_name=thermostat_name,
                                           application_key=application_key)
        finally:
            if pyecobee_db is not None:
                pyecobee_db.close()

        if not ecobee_service.authorization_token:
            authorize(ecobee_service)
        if not ecobee_service.access_token:
            request_tokens(ecobee_service)

        now_utc = datetime.now(pytz.utc)
        if now_utc > ecobee_service.refresh_token_expires_on:
            authorize(ecobee_service)
            request_tokens(ecobee_service)
        elif now_utc > ecobee_service.access_token_expires_on:
            refresh_tokens(ecobee_service)

        logger.debug(ecobee_service.pretty_format())

        """logger.info(
            'Access Token             => {0}\n'
            'Access Token Expires On  => {1}\n'
            'Refresh Token            => {2}\n'
            'Refresh Token Expires On => {3}'.format(ecobee_service.access_token,
                                                     ecobee_service.access_token_expires_on,
                                                     ecobee_service.refresh_token,
                                                     ecobee_service.refresh_token_expires_on))"""

        """remove_hierarchy_users_response = ecobee_service.remove_hierarchy_users(
            set_path='/',
            users=[
                HierarchyUser(
                    user_name='todelete@hierarchy.com'
                ),
                HierarchyUser(
                    user_name='todelete2@hierarchy.com'
                )])
        logger.info(remove_hierarchy_users_response.pretty_format())
        assert remove_hierarchy_users_response.status.code == 0, (
            'Failure while executing remove_hierarchy_users:\n{0}'.format(
                remove_hierarchy_users_response.pretty_format()))"""

        # Unregister Hierarchy Users
        """unregister_hierarchy_users_response = ecobee_service.unregister_hierarchy_users(
            users=[
                HierarchyUser(
                    user_name='todelete@hierarchy.com'),
                HierarchyUser(
                    user_name='todelete2@hierarchy.com')])"""

        """update_hierarchy_users_response = update_hierarchy_users_response = ecobee_service.update_hierarchy_users(
            users=[HierarchyUser(
                user_name='user1@update.com',
                first_name='Updated',
                last_name='User',
                phone='222-333-4444',
                email_alerts=False)
            ], privileges=[
                HierarchyPrivilege(set_path='/MainNode',
                                   user_name='user1@update.com',
                                   allow_view=True),
                HierarchyPrivilege(set_path='/MainNode',
                                   user_name='user2@update.com',
                                   allow_view=True),
                HierarchyPrivilege(set_path='/OtherNode',
                                   user_name='user2@update.com',
                                   allow_view=True)])"""
        # Register Hierarchy Thermostat
        """register_hierarchy_thermostats_response = ecobee_service.register_hierarchy_thermostats(set_path='/OtherNode',
                                                                                                thermostats=(
                                                                                                    '123456789012,'
                                                                                                    '123456789013'))"""

        # Unregister Hierarchy Thermostat
        """unregister_hierarchy_thermostats_response = ecobee_service.unregister_hierarchy_thermostats(
            thermostats='123456789012,123456789013')"""

        # Move Hierarchy Thermostat
        """move_hierarchy_thermostats_response = ecobee_service.move_hierarchy_thermostats(set_path='/MainNode',
                                                                                        to_path='/OtherNode',
                                                                                        thermostats=('123456789012,'
                                                                                                     '123456789013'))"""

        # Assign Hierarchy Thermostat
        """assign_hierarchy_thermostats_response = ecobee_service.assign_hierarchy_thermostats(set_path='/MainNode',
                                                                                            thermostats=('123456789012,'
                                                                                                         '123456789013'))"""

        # List Demand EcobeeResponse
        """list_demand_responses_response = ecobee_service.list_demand_responses()"""

        # Issue Demand EcobeeResponse
        """issue_demand_response_response = ecobee_service.issue_demand_response(
            selection=Selection(
                selection_type=SelectionType.MANAGEMENT_SET.value,
                selection_match='/'),
            demand_response=DemandResponse(
                name='myDR',
                message='This is a DR!',
                event=Event(
                    heat_hold_temp=790,
                    end_time='11:37:18',
                    end_date='2011-01-10',
                    name='apiDR',
                    type='useEndTime',
                    cool_hold_temp=790,
                    start_date='2011-01-09',
                    start_time='11:37:18',
                    is_temperature_absolute=True)))"""

        # Cancel Demand EcobeeResponse
        """cancel_demand_response_response = ecobee_service.cancel_demand_response(
            demand_response_ref='c253a12e0b3c3c93800095')"""

        # Issue Demand Management
        """issue_demand_management_response = ecobee_service.issue_demand_managements(
            selection=Selection(
                selection_type=SelectionType.MANAGEMENT_SET.value,
                selection_match='/'),
            demand_managements=[
                DemandManagement(
                    date='2012-01-01',
                    hour=5,
                    temp_offsets=[20, 20, 20, 0, 0, 0, 0, -20, -20, -20, 0, 0]),
                DemandManagement(
                    date='2012-01-01',
                    hour=6,
                    temp_offsets=[0, 0, 20, 20, 0, 0, 0, 0, 0, -20, -20, -20])])"""

        # Create Runtime Report Job
        """create_runtime_report_job_response = ecobee_service.create_runtime_report_job(
            selection=Selection(
                selection_type=SelectionType.THERMOSTATS.value,
                selection_match='123456789012'),
            start_date=date(2016, 7, 1),
            end_date=date(2016, 10, 1),
            columns='zoneCalendarEvent,zoneHvacMode,zoneHeatTemp,zoneCoolTemp,zoneAveTemp,dmOffset')"""

        # List Runtime Report Job Status
        """list_runtime_report_job_status_response = ecobee_service.list_runtime_report_job_status(job_id='123')"""

        # Cancel Runtime Report Job
        """cancel_runtime_report_response = ecobee_service.cancel_runtime_report_job(job_id='123')"""

        """class_ = EcobeeListRuntimeReportJobStatusResponse
        response = dictionary_to_object(
            {class_.__name__: json.loads(open('list_runtime_report_job_response.txt').read())},
            {class_.__name__: class_},
            {class_.__name__: None},
            is_top_level=True)
        logger.info(response.pretty_format())
        sys.exit(0)"""

        # vacation_name = 'Vacation_{0}.{1}'.format(python_version[0], python_version[1])
        # test_create_vacation(ecobee_service, vacation_name)
        #
        # message = 'Hello Pyecobee_{0}.{1}'.format(python_version[0], python_version[1])
        # test_send_message(ecobee_service, message)
        #
        # test_set_hold(ecobee_service)
        #
        # fan_min_on_time = 15
        # test_update_thermosats(ecobee_service, fan_min_on_time)
        #
        thermostat = test_request_thermostats_all(ecobee_service)
        #
        # events = [event for event in thermostat.events if event.name == vacation_name]
        # assert events, 'Failure while asserting create_vacation'
        #
        # alerts = [alert for alert in thermostat.alerts if alert.text == message]
        # assert alerts, 'Failure while asserting send_message.'
        #
        # assert thermostat.settings.fan_min_on_time == fan_min_on_time, 'Failure while asserting update_thermostats'
        #
        # test_delete_vacation(ecobee_service, vacation_name)
        # test_acknowledge(ecobee_service, thermostat, alerts[0])
        # test_resume_program(ecobee_service)
        #
        # thermostat = test_request_thermostats_all(ecobee_service)
        # events = [event for event in thermostat.events if event.name == vacation_name]
        # assert not events, 'Failure while asserting delete_vacation'
        #
        # alerts = [alert for alert in thermostat.alerts if alert.text == message]
        # assert not alerts, 'Failure while asserting acknowledge.'
        #
        test_request_thermostats_summary(ecobee_service)
        # test_request_meter_reports(ecobee_service, thermostat)
        # test_runtime_reports(ecobee_service, thermostat)
        #
        # groups = [Group(group_name='Group_{0}.{1}'.format(python_version[0], python_version[1]),
        #                 synchronize_alerts=True,
        #                 synchronize_vacation=True,
        #                 thermostats=[thermostat.identifier])]
        # groups = test_update_groups(ecobee_service, groups)
        #
        # groups = [Group(group_name='Group_{0}.{1}'.format(python_version[0], python_version[1]),
        #                 group_ref=groups[0].group_ref)]
        # groups = test_update_groups(ecobee_service, groups)
        # groups = test_request_groups(ecobee_service)

        logger.info('All tests passed!!!')
    except EcobeeException:
        logger.exception(traceback.format_exc())


if __name__ == '__main__':
    main()
