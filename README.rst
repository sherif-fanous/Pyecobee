Pyecobee: A Python implementation of the `ecobee API <https://www.ecobee.com/home/developer/api/introduction/index.shtml>`_
===========================================================================================================================

Introduction
============
Pyecobee is a simple, elegant, and object oriented implementation of the ecobee API in Python. It is compatible with Python 2.6/2.7/3.3/3.4/3.5/3.6

**Warning:** Pyecobee has been tested with an ecobee Smart Si. Though the following methods have not been tested I
believe they should work find. Please create an `issue <https://github.com/sfanous/Pyecobee/issues>`_ or even better
create a `pull request <https://github.com/sfanous/Pyecobee/pull/new/master>`_ if you encounter an issue with any of
them.

- control_plug: I don't own an ecobee smart plug, so couldn't test this function
- reset_preferences: I didn't want to wipe my thermostat's settings
- set_occupied: Can only be used by an EMS thermostat
- update_sensor: Requires an ecobee3 or ecobee4 thermostat
- All Hierarchy requests: Accessible to EMS and Utility accounts only
    - list_sets
    - list_users
    - add_set
    - remove_set
    - rename_set
    - move_set
    - add_user
    - remove_user
    - unregister_user
    - update_user
    - register_thermostat
    - unregister_thermostat
    - move_thermostat
    - assign_thermostat
- All Utility requests: Accessible to Utility accounts only
    - list_demand_response
    - issue_demand_response
    - cancel_demand_response
    - issue_demand_management
- All Runtime Report Job requests: Accessible to Utility accounts only
    - create_runtime_report_job
    - list_runtime_report_job_status
    - cancel_runtime_report_job

**Disclaimer:** Any ecobee API Keys, Authorization/Access/Refresh Tokens used in the following examples are fake.

JSON Vs Objects
===============
Whereas JSON notation is used for the serialization/deserialization of request/response objects sent to and from the
ecobee API, Pyecobee's interface is based on core Python data types and user defined objects instead. Pyecobee
handles the serialization of Python objects into JSON request objects and deserialization of JSON response objects
into Python objects thus completely alleviating the developer's need to create/parse JSON objects.

Pyecobee response from an authorize request
-------------------------------------------

.. code-block:: python

    authorize_response = ecobee_service.authorize()
    pin = authorize_response.ecobee_pin
    code = authorize_response.code
    scope = authorize_response.scope
    expires_in = authorize_response.expires_in
    interval = authorize_response.interval

Installation
============
To install Pyecobee:

.. code-block:: bash

    $ pip install pyecobee

Enjoy.


Documentation
=============
Pyecobee comes with extensive documentation. Use dir and help to explore all the details.
.. code-block:: python

    >>> from pyecobee import *
    >>> dir(EcobeeService)
    >>> help(EcobeeService)

General usage
=============
The **EcobeeService** class provides the ecobee API implementation.

EcobeeService Class Diagram
---------------------------
.. image:: https://cdn.rawgit.com/sfanous/33688c4e0db84fc062f56ee1b7ffe444/raw/216366455a9e200c278583c42e3b64c28d2b886b/EcobeeService.svg

To use Pyecobee follow these steps

- Import the modules
- Instantiate an EcobeeService object
- Complete the authorization sequence if required (authorize + request_tokens)
- Refresh tokens if required (refresh_tokens)
- Invoke the needed ecobee API requests/functions

All Pyecobee user defined objects overload __repr__, __str__, and implement a pretty_format method.

.. code-block:: python

    >>> repr(authorize_response)
    AuthorizeResponse(ecobee_pin='bv29', code='uiNQok9Uhy5iScG4gncCAilcFUMK0zWT', scope='smartWrite', expires_in=9, interval=30)

    >>> str(authorize_response)
    AuthorizeResponse(ecobeePin=bv29, code=uiNQok9Uhy5iScG4gncCAilcFUMK0zWT, scope=smartWrite, expires_in=9, interval=30)

    >>> authorize_response.pretty_format()
    AuthorizeResponse(
      ecobeePin=bv29,
      code=uiNQok9Uhy5iScG4gncCAilcFUMK0zWT,
      scope=smartWrite,
      expires_in=9,
      interval=30
    )

Import the modules
------------------
.. code-block:: python

    from pyecobee import *

Instantiate an EcobeeService object
-----------------------------------

.. code-block:: python

    ecobee_service = EcobeeService(thermostat_name='My Thermostat',
                                   application_key='jiNXJ2Q6dyeAPXxy4HsFGUp1nK94C9VF')

Authorization & Token Requests
------------------------------
Authorize
^^^^^^^^^

.. code-block:: python

    authorize_response = ecobee_service.authorize()
    logger.info(authorize_response.pretty_format())
    logger.info('Authorization Token => {0}'.format(ecobee_service.authorization_token))

A successful invocation of authorize() returns an EcobeeAuthorizeResponse instance

EcobeeAuthorizeResponse Class Diagram
"""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/4263de2c38a41c2023234932ba6dd8c4/raw/ff067f69ad160ced5ea10602b6ac57f562be98f4/EcobeeAuthorizeResponse.svg

Request Tokens
^^^^^^^^^^^^^^

.. code-block:: python

    token_response = ecobee_service.request_tokens()
    logger.info(token_response.pretty_format())
    logger.info(
            'Access Token => {0}\n'
            'Access Token Expires On => {1}\n'
            'Refresh Token => {2}\n'
            'Refresh Token Expires On => {3}'.format(ecobee_service.access_token,
                                                     ecobee_service.access_token_expires_on,
                                                     ecobee_service.refresh_token,
                                                     ecobee_service.refresh_token_expires_on))

A successful invocation of request_tokens() returns an EcobeeTokenResponse instance

EcobeeTokenResponse Class Diagram
"""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/61c4e7fe3bbcae96b237da1cfcc2fa63/raw/350ca74d19e01d2852c37b54ac48459bf6916745/EcobeeTokensResponse.svg

Refresh Tokens
^^^^^^^^^^^^^^

.. code-block:: python

    token_response = ecobee_service.refresh_tokens()
    logger.info(token_response.pretty_format())
    logger.info(
            'Access Token => {0}\n'
            'Access Token Expires On => {1}\n'
            'Refresh Token => {2}\n'
            'Refresh Token Expires On => {3}'.format(ecobee_service.access_token,
                                                     ecobee_service.access_token_expires_on,
                                                     ecobee_service.refresh_token,
                                                     ecobee_service.refresh_token_expires_on))

A successful invocation of refresh_tokens() returns an EcobeeTokenResponse instance

EcobeeTokenResponse Class Diagram
"""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/61c4e7fe3bbcae96b237da1cfcc2fa63/raw/350ca74d19e01d2852c37b54ac48459bf6916745/EcobeeTokensResponse.svg

Thermostat Requests
--------------------
Request Thermostat Summary
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    thermostat_summary_response = ecobee_service.request_thermostats_summary(selection=Selection(
            selection_type=SelectionType.REGISTERED.value,
            selection_match='',
            include_equipment_status=True))
    logger.info(thermostat_summary_response.pretty_format())

A successful invocation of request_thermostats_summary() returns an EcobeeThermostatsSummaryResponse instance

EcobeeThermostatsSummaryResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/957474de7596100c37aab58dcfe81a1a/raw/1e5c8a5b1143f163dd8ee81f314e92d247be361f/EcobeeThermostatsSummaryResponse.svg

Request Thermostats
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Only set the include options you need to True. I've set most of them to True for illustrative purposes only.
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='', include_alerts=True,
                          include_device=True, include_electricity=True, include_equipment_status=True,
                          include_events=True, include_extended_runtime=True, include_house_details=True,
                          include_location=True, include_management=True, include_notification_settings=True,
                          include_oem_cfg=False, include_privacy=False, include_program=True, include_reminders=True,
                          include_runtime=True, include_security_settings=False, include_sensors=True,
                          include_settings=True, include_technician=True, include_utility=True, include_version=True,
                          include_weather=True)
    thermostat_response = ecobee_service.request_thermostats(selection)
    logger.info(thermostat_response.pretty_format())
    assert thermostat_response.status.code == 0, 'Failure while executing request_thermostats:\n{0}'.format(
        thermostat_response.pretty_format())

A successful invocation of request_thermostats() returns an EcobeeThermostatResponse instance

EcobeeThermostatResponse Class Diagram
""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/a674640718e63fdb2f1cb5ed9c2f2466/raw/b69664237635ce914f39f397c29899af408079a6/EcobeeThermostatResponse.svg

Update Thermostat
^^^^^^^^^^^^^^^^^

.. code-block:: python

    update_thermostat_response = ecobee_service.update_thermostats(
            selection=Selection(
                selection_type=SelectionType.REGISTERED.value,
                selection_match=''),
            thermostat=Thermostat(
                settings=Settings(
                    hvac_mode='off')),
            functions=[
                Function(
                    type='deleteVacation',
                    params={'name': 'My vacation'})])
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing update_thermostats:\n{0}'.format(
        update_thermostat_response.pretty_format())

A successful invocation of update_thermostats() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Report Requests
---------------
Meter Report
^^^^^^^^^^^^

.. code-block:: python

    eastern = timezone('US/Eastern')
    meter_reports_response = ecobee_service.request_meter_reports(
            selection=Selection(
                selection_type=SelectionType.THERMOSTATS.value,
                selection_match='123456789012'),
            start_date_time=eastern.localize(datetime(2013, 4, 4, 0, 0, 0), is_dst=True),
            end_date_time=eastern.localize(datetime(2013, 4, 4, 23, 59, 0), is_dst=True))
    logger.info(meter_report_response.pretty_format())
    assert meter_report_response.status.code == 0, 'Failure while executing request_meter_reports:\n{0}'.format(
        meter_report_response.pretty_format())

A successful invocation of request_meter_reports() returns an EcobeeMeterReportsResponse instance

EcobeeMeterReportsResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/6abbae0f9c85d75304557d306b8777e6/raw/8b9e6c33d2b609b9112a8369b5ef397082cf45d4/EcobeeMeterReportsResponse.svg

Runtime Report
^^^^^^^^^^^^^^

.. code-block:: python

    eastern = timezone('US/Eastern')
    runtime_report_response = ecobee_service.request_runtime_reports(
            selection=Selection(
                selection_type=SelectionType.THERMOSTATS.value,
                selection_match='123456789012'),
            start_date_time=eastern.localize(datetime(2010, 1, 1, 0, 0, 0), is_dst=False),
            end_date_time=eastern.localize(datetime(2010, 1, 2, 0, 0, 0), is_dst=False),
            columns='auxHeat1,auxHeat2,auxHeat3,compCool1,compCool2,compHeat1,compHeat2,dehumidifier,dmOffset,'
                    'economizer,fan,humidifier,hvacMode,outdoorHumidity,outdoorTemp,sky,ventilator,wind,zoneAveTemp,'
                    'zoneCalendarEvent,zoneClimate,zoneCoolTemp,zoneHeatTemp,zoneHumidity,zoneHumidityHigh,'
                    'zoneHumidityLow,zoneHvacMode,zoneOccupancy')
    logger.info(runtime_report_response.pretty_format())
    assert runtime_report_response.status.code == 0, 'Failure while executing request_runtime_reports:\n{0}'.format(
        runtime_report_response.pretty_format())

A successful invocation of request_runtime_reports() returns an EcobeeRuntimeReportsResponse instance

EcobeeRuntimeReportsResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/5816b010e7207d756984805521015ba0/raw/e219e0d91ffe1196f1e731cd54ec91c638455deb/EcobeeRuntimeReportsResponse.svg

Group Requests
--------------
Request Groups
^^^^^^^^^^^^^^

.. code-block:: python

    group_response = ecobee_service.request_groups(
            selection=Selection(
                selection_type=SelectionType.REGISTERED.value))
    logger.info(group_response.pretty_format())
    assert group_response.status.code == 0, 'Failure while executing request_groups:\n{0}'.format(
        group_response.pretty_format())

A successful invocation of request_groups() returns an EcobeeGroupsResponse instance

EcobeeGroupsResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/72918aca65419a8edecbb263623738a1/raw/398f60d6eba507f0072dfbc684cc2b015028179b/EcobeeGroupsResponse.svg

Update Groups
^^^^^^^^^^^^^

.. code-block:: python

    # Create Groups
    group_response = ecobee_service.update_groups(
            selection=Selection(
                selection_type=SelectionType.REGISTERED.value),
            groups=[
                Group(
                    group_ref='3d03a26fd80001',
                    group_name='ground_floor',
                    synchronize_alerts=True,
                    synchronize_vacation=True,
                    thermostats=[
                        '123456789101']),
                Group(
                    group_ref='3bb5a91b180001',
                    group_name='first_floor',
                    synchronize_reset=True,
                    synchronize_vacation=True,
                    thermostats=[
                        '123456789102'])])
    logger.info(group_response.pretty_format())
    assert group_response.status.code == 0, 'Failure while executing update_groups:\n{0}'.format(
        group_response.pretty_format())

    # Update a Group
    group_response = ecobee_service.update_groups(
            selection=Selection(
                selection_type=SelectionType.REGISTERED.value),
            groups=[
                Group(
                    group_ref='3d03a26fd80001',
                    synchronize_system_mode=True)])
    logger.info(group_response.pretty_format())
    assert group_response.status.code == 0, 'Failure while executing update_groups:\n{0}'.format(
        group_response.pretty_format())

    # Delete a group (Set the thermostats parameter of the group to an empty list)
    group_response = ecobee_service.update_groups(
            selection=Selection(
                selection_type=SelectionType.REGISTERED.value),
            groups=[
                Group(
                    group_ref='3d03a26fd80001',
                    thermostats=[])])
    logger.info(group_response.pretty_format())
    assert group_response.status.code == 0, 'Failure while executing update_groups:\n{0}'.format(
        group_response.pretty_format())

A successful invocation of request_groups() returns an EcobeeGroupsResponse instance

EcobeeGroupsResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/72918aca65419a8edecbb263623738a1/raw/398f60d6eba507f0072dfbc684cc2b015028179b/EcobeeGroupsResponse.svg

Hierarchy Set Requests
----------------------
List Hierarchy Sets
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    list_hierarchy_sets_response = ecobee_service.list_hierarchy_sets(set_path='/',
                                                                      recursive=True,
                                                                      include_privileges=True,
                                                                      include_thermostats=True)
    logger.info(list_hierarchy_sets_response.pretty_format())
    assert list_hierarchy_sets_response.status.code == 0, 'Failure while executing list_hierarchy_sets:\n{0}'.format(
        list_hierarchy_sets_response.pretty_format())

A successful invocation of list_hierarchy_sets() returns an EcobeeListHierarchySetsResponse instance

EcobeeListHierarchySetsResponse Class Diagram
"""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/a68c63860b11e4b1c51193a6cbd2f817/raw/de90f47ce357c85e58559d73bd59bee1892057ed/EcobeeListHierarchySetsResponse.svg

Add Hierarchy Set
^^^^^^^^^^^^^^^^^

.. code-block:: python

    add_hierarchy_set_response = ecobee_service.add_hierarchy_set(set_name='NewSet',
                                                                  parent_path='/')
    logger.info(add_hierarchy_set_response.pretty_format())
    assert add_hierarchy_set_response.status.code == 0, 'Failure while executing add_hierarchy_set:\n{0}'.format(
        add_hierarchy_set_response.pretty_format())

A successful invocation of add_hierarchy_set() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Remove Hierarchy Set
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    remove_hierarchy_set_response = ecobee_service.remove_hierarchy_set(set_path='/NewSet')
    logger.info(remove_hierarchy_set_response.pretty_format())
    assert remove_hierarchy_set_response.status.code == 0, 'Failure while executing remove_hierarchy_set:\n{0}'.format(
        remove_hierarchy_set_response.pretty_format())

A successful invocation of remove_hierarchy_set() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Rename Hierarchy Set
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    rename_hierarchy_set_response = ecobee_service.rename_hierarchy_set(set_path='/NewSet',
                                                                        new_name='ToRename')
    logger.info(rename_hierarchy_set_response.pretty_format())
    assert rename_hierarchy_set_response.status.code == 0, 'Failure while executing rename_hierarchy_set:\n{0}'.format(
        rename_hierarchy_set_response.pretty_format())

A successful invocation of rename_hierarchy_set() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Move Hierarchy Set
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    move_hierarchy_set_response = ecobee_service.move_hierarchy_set(set_path='/ToMove',
                                                                    to_path='MainNode')
    logger.info(move_hierarchy_set_response.pretty_format())
    assert move_hierarchy_set_response.status.code == 0, 'Failure while executing move_hierarchy_set:\n{0}'.format(
        move_hierarchy_set_response.pretty_format())

A successful invocation of move_hierarchy_set() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Hierarchy User Requests
-----------------------
List Hierarchy Users
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    list_hierarchy_users_response = ecobee_service.list_hierarchy_users(set_path='/',
                                                                        recursive=True,
                                                                        include_privileges=True)
    logger.info(list_hierarchy_users_response.pretty_format())
    assert list_hierarchy_users_response.status.code == 0, 'Failure while executing list_hierarchy_users:\n{0}'.format(
        list_hierarchy_users_response.pretty_format())

A successful invocation of list_hierarchy_users() returns an EcobeeListHierarchyUsersResponse instance

EcobeeListHierarchyUsersResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/6ab4920c897067424001148f881a1591/raw/acdbe370a54dc50b56515f4797c782e30a0d4fd8/EcobeeListHierarchyUsersResponse.svg

Add Hierarchy Users
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    add_hierarchy_users_response = ecobee_service.add_hierarchy_users(
        users=[
            HierarchyUser(
                user_name='new@user1.com',
                first_name='User',
                last_name='1'),
            HierarchyUser(
                user_name='new@user2.com',
                first_name='User',
                last_name='2')],
        privileges=[
            HierarchyPrivilege(
                set_path='/MainNode',
                user_name='new@user1.com',
                allow_view=True),
            HierarchyPrivilege(
                set_path='/OtherNode',
                user_name='new@user1.com',
                allow_view=True)])
        logger.info(add_hierarchy_users_response.pretty_format())
        assert add_hierarchy_users_response.status.code == 0, (
            'Failure while executing add_hierarchy_users:\n{0}'.format(
             add_hierarchy_users_response.pretty_format()))

A successful invocation of add_hierarchy_users() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Remove Hierarchy Users
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    remove_hierarchy_users_response = ecobee_service.remove_hierarchy_users(
        set_path='/',
        users=[
            HierarchyUser(
                user_name='todelete@hierarchy.com'),
            HierarchyUser(
                user_name='todelete2@hierarchy.com')])
    logger.info(remove_hierarchy_users_response.pretty_format())
    assert remove_hierarchy_users_response.status.code == 0, (
        'Failure while executing remove_hierarchy_users:\n{0}'.format(
            remove_hierarchy_users_response.pretty_format()))

A successful invocation of remove_hierarchy_users() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Unregister Hierarchy Users
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    unregister_hierarchy_users_response = ecobee_service.unregister_hierarchy_users(
        users=[
            HierarchyUser(
                user_name='todelete@hierarchy.com'),
            HierarchyUser(
                user_name='todelete2@hierarchy.com')])
    logger.info(unregister_hierarchy_users_response.pretty_format())
    assert unregister_hierarchy_users_response.status.code == 0, (
        'Failure while executing unregister_hierarchy_users_response:\n{0}'.format(
            unregister_hierarchy_users_response.pretty_format()))

A successful invocation of unregister_hierarchy_users() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Update Hierarchy Users
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    update_hierarchy_users_response = update_hierarchy_users_response = ecobee_service.update_hierarchy_users(
        users=[
            HierarchyUser(
                user_name='user1@update.com',
                first_name='Updated',
                last_name='User',
                phone='222-333-4444',
                email_alerts=False)],
        privileges=[
            HierarchyPrivilege(
                set_path='/MainNode',
                user_name='user1@update.com',
                allow_view=True),
            HierarchyPrivilege(
                set_path='/MainNode',
                user_name='user2@update.com',
                allow_view=True),
            HierarchyPrivilege(
                set_path='/OtherNode',
                user_name='user2@update.com',
                allow_view=True)])
    logger.info(update_hierarchy_users_response.pretty_format())
    assert update_hierarchy_users_response.status.code == 0, (
        'Failure while executing update_hierarchy_users_response:\n{0}'.format(
            update_hierarchy_users_response.pretty_format()))

A successful invocation of update_hierarchy_users() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Hierarchy Thermostat Requests
-----------------------------
Register Thermostat
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    register_hierarchy_thermostats_response = ecobee_service.register_hierarchy_thermostats(set_path='/OtherNode',
                                                                                            thermostats=(
                                                                                                '123456789012,'
                                                                                                '123456789013'))
    logger.info(register_hierarchy_thermostats_response.pretty_format())
    assert register_hierarchy_thermostats_response.status.code == 0, (
        'Failure while executing register_hierarchy_thermostats_response:\n{0}'.format(
            register_hierarchy_thermostats_response.pretty_format()))

A successful invocation of register_hierarchy_thermostats() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Unregister Thermostat
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    unregister_hierarchy_thermostats_response = ecobee_service.unregister_hierarchy_thermostats(
        thermostats='123456789012,123456789013')
    logger.info(unregister_hierarchy_thermostats_response.pretty_format())
    assert unregister_hierarchy_thermostats_response.status.code == 0, (
        'Failure while executing unregister_hierarchy_thermostats_response:\n{0}'.format(
            unregister_hierarchy_thermostats_response.pretty_format()))

A successful invocation of unregister_hierarchy_thermostats() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Move Thermostat
^^^^^^^^^^^^^^^

.. code-block:: python

    move_hierarchy_thermostats_response = ecobee_service.move_hierarchy_thermostats(set_path='/MainNode',
                                                                                    to_path='/OtherNode',
                                                                                    thermostats=('123456789012,'
                                                                                                 '123456789013'))
    logger.info(move_hierarchy_thermostats_response.pretty_format())
    assert move_hierarchy_thermostats_response.status.code == 0, (
        'Failure while executing move_hierarchy_thermostats_response:\n{0}'.format(
            move_hierarchy_thermostats_response.pretty_format()))

A successful invocation of move_hierarchy_thermostats() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Assign Thermostat
^^^^^^^^^^^^^^^^^

.. code-block:: python

    assign_hierarchy_thermostats_response = ecobee_service.assign_hierarchy_thermostats(set_path='/MainNode',
                                                                                        thermostats=('123456789012,'
                                                                                                     '123456789013'))
    logger.info(assign_hierarchy_thermostats_response.pretty_format())
    assert assign_hierarchy_thermostats_response.status.code == 0, (
        'Failure while executing assign_hierarchy_thermostats_response:\n{0}'.format(
            assign_hierarchy_thermostats_response.pretty_format()))

A successful invocation of assign_hierarchy_thermostats() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Utility Requests
----------------
List Demand Responses
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    list_demand_responses_response = ecobee_service.list_demand_responses()
    logger.info(list_demand_responses_response.pretty_format())
    assert list_demand_responses_response.status.code == 0, (
        'Failure while executing list_demand_responses_response:\n{0}'.format(
            list_demand_responses_response.pretty_format()))

A successful invocation of list_demand_responses() returns an EcobeeListDemandResponsesResponse instance

EcobeeListDemandResponsesResponse Class Diagram
"""""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/c60426de08616e85843dd7528956c204/raw/dbfd645ac49d4db5750c7a88698bbc5a3ba0e09c/EcobeeListDemandResponsesResponse.svg

Issue Demand Response
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    issue_demand_response_response = ecobee_service.issue_demand_response(
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
                is_temperature_absolute=True)))
    logger.info(issue_demand_response_response.pretty_format())
    assert issue_demand_response_response.status.code == 0, (
        'Failure while executing issue_demand_response_response:\n{0}'.format(
            issue_demand_response_response.pretty_format()))

A successful invocation of issue_demand_response() returns an EcobeeIssueDemandResponsesResponse instance

EcobeeIssueDemandResponsesResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/7b8cc714ba9fb7d00e6ad70dc2fdc618/raw/30c32230fc580d4f9f437985f325c9994682c585/EcobeeIssueDemandResponsesResponse.svg

Cancel Demand Response
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    cancel_demand_response_response = ecobee_service.cancel_demand_response(
        demand_response_ref='c253a12e0b3c3c93800095')
    logger.info(cancel_demand_response_response.pretty_format())
    assert cancel_demand_response_response.status.code == 0, (
        'Failure while executing cancel_demand_response_response:\n{0}'.format(
            cancel_demand_response_response.pretty_format()))

A successful invocation of cancel_demand_response() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Issue Demand Management
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    issue_demand_management_response = ecobee_service.issue_demand_managements(
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
                temp_offsets=[0, 0, 20, 20, 0, 0, 0, 0, 0, -20, -20, -20])])
    logger.info(issue_demand_management_response.pretty_format())
    assert issue_demand_management_response.status.code == 0, (
        'Failure while executing issue_demand_management_response:\n{0}'.format(
            issue_demand_management_response.pretty_format()))

Runtime Report Job Requests
---------------------------
Create Runtime Report Job
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    create_runtime_report_job_response = ecobee_service.create_runtime_report_job(
        selection=Selection(
            selection_type=SelectionType.THERMOSTATS.value,
            selection_match='123456789012'),
        start_date=date(2016, 7, 1),
        end_date=date(2016, 10, 1),
        columns='zoneCalendarEvent,zoneHvacMode,zoneHeatTemp,zoneCoolTemp,zoneAveTemp,dmOffset')
    logger.info(create_runtime_report_job_response.pretty_format())
    assert create_runtime_report_job_response.status.code == 0, (
        'Failure while executing create_runtime_report_job_response:\n{0}'.format(
            create_runtime_report_job_response.pretty_format()))

A successful invocation of create_runtime_report_job() returns an EcobeeCreateRuntimeReportJobResponse instance

EcobeeCreateRuntimeReportJobResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/e19e2d2e529a780baad57d91bbc74d3a/raw/a9347aa590d37c5f71f9ea6bbfffc068ae75ae18/EcobeeCreateRuntimeReportJobResponse.svg

List Runtime Report Job Status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    list_runtime_report_job_status_response = ecobee_service.list_runtime_report_job_status(job_id='123')
    logger.info(list_runtime_report_job_status_response.pretty_format())
    assert list_runtime_report_job_status_response.status.code == 0, (
        'Failure while executing list_runtime_report_job_status_response:\n{0}'.format(
            list_runtime_report_job_status_response.pretty_format()))

A successful invocation of list_runtime_report_job_status() returns an EcobeeListRuntimeReportJobStatusResponse instance

EcobeeListRuntimeReportJobStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/45e7a445e3f643be0439438d0b66821e/raw/68f8b9b0902b2b204a126561c3eba39a7c729fb5/EcobeeListRuntimeReportJobStatusResponse.svg

Cancel Runtime Report Job
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    cancel_runtime_report_response = ecobee_service.cancel_runtime_report_job(job_id='123')
    logger.info(cancel_runtime_report_response.pretty_format())
    assert cancel_runtime_report_response.status.code == 0, (
        'Failure while executing cancel_runtime_report_response:\n{0}'.format(
            cancel_runtime_report_response.pretty_format()))

A successful invocation of cancel_runtime_report_job() returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
""""""""""""""""""""""""""""""""""
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Thermostat Functions
--------------------
A successful invocation of any function returns an EcobeeStatusResponse instance

EcobeeStatusResponse Class Diagram
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. image:: https://cdn.rawgit.com/sfanous/ce50523143e93b25d0ac9954aded53e5/raw/db56f013eb88a64287e45652f7b14a063cf501fb/EcobeeStatusResponse.svg

Send Message
^^^^^^^^^^^^

.. code-block:: python

    update_thermostat_response = ecobee_service.send_message('Hello World')
    logger.info(update_thermostat_response.pretty_format())
    assert thermostat_response.status.code == 0, 'Failure while executing request_thermostats:\n{0}'.format(
        thermostat_response.pretty_format())

Acknowledge
^^^^^^^^^^^

.. code-block:: python

    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='', include_alerts=True)
    thermostat_response = ecobee_service.request_thermostats(selection)
    thermostat = thermostat_response.thermostat_list[0]
    alerts = [alert for alert in thermostat.alerts if alert.text == message]

    update_thermostat_response = ecobee_service.acknowledge(thermostat_identifier=thermostat.identifier,
                                                            ack_ref=alerts[0].acknowledge_ref,
                                                            ack_type=AckType.ACCEPT)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing acknowledge:\n{0}'.format(
        update_thermostat_response.pretty_format())

Set Hold
^^^^^^^^

.. code-block:: python

    # Simplest form
    update_thermostat_response = ecobee_service.set_hold(hold_climate_ref='away', hold_type=HoldType.NEXT_TRANSITION)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing set_hold:\n{0}'.format(
        update_thermostat_response.pretty_format())

    # Using specific start/end date and time
    eastern = timezone('US/Eastern')
    update_thermostat_response = ecobee_service.set_hold(hold_climate_ref='away',
                                                         start_date_time=eastern.localize(datetime(
                                                             2017, 5, 10, 13, 0, 0),
                                                             is_dst=True),
                                                         end_date_time=eastern.localize(datetime(
                                                             2017, 5, 10, 14, 0, 0),
                                                             is_dst=True),
                                                         hold_type=HoldType.DATE_TIME)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing set_hold:\n{0}'.format(
        update_thermostat_response.pretty_format())

    # Using duration
    eastern = timezone('US/Eastern')
    update_thermostat_response = ecobee_service.set_hold(hold_climate_ref='away',
                                                         start_date_time=eastern.localize(datetime(
                                                             2017, 5, 10, 13, 0, 0),
                                                             is_dst=True),
                                                         hold_type=HoldType.HOLD_HOURS,
                                                         hold_hours=1)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing set_hold:\n{0}'.format(
        update_thermostat_response.pretty_format())

    # Specifically the cooling temperature to use and hold indefinitely
    update_thermostat_response = ecobee_service.set_hold(cool_hold_temp=65,  hold_type=HoldType.INDEFINITE)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing set_hold:\n{0}'.format(
        update_thermostat_response.pretty_format())

    # Specifically the heating temperature to use and hold indefinitely
    update_thermostat_response = ecobee_service.set_hold(heat_hold_temp=72,  hold_type=HoldType.INDEFINITE)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing set_hold:\n{0}'.format(
        update_thermostat_response.pretty_format())

Resume Program
^^^^^^^^^^^^^^

.. code-block:: python

    update_thermostat_response = ecobee_service.resume_program(resume_all=False)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing resume_program:\n{0}'.format(
        update_thermostat_response.pretty_format())

Create Vacation
^^^^^^^^^^^^^^^

.. code-block:: python

    eastern = timezone('US/Eastern')
    update_thermostat_response = ecobee_service.create_vacation(name='Christmas Vacation!',
                                                                cool_hold_temp=104,
                                                                heat_hold_temp=59,
                                                                start_date_time=eastern.localize(datetime(
                                                                    2017, 12, 23, 10, 0, 0),
                                                                    is_dst=True),
                                                                end_date_time=eastern.localize(datetime(
                                                                    2017, 12, 28, 17, 0, 0),
                                                                    is_dst=True),
                                                                fan_mode=FanMode.AUTO,
                                                                fan_min_on_time=0)
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing create_vacation:\n{0}'.format(
        update_thermostat_response.pretty_format())

Delete Vacation
^^^^^^^^^^^^^^^

.. code-block:: python

    update_thermostat_response = ecobee_service.delete_vacation(name='Christmas Vacation!')
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing delete_vacation:\n{0}'.format(
        update_thermostat_response.pretty_format())

Reset Preferences
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Danger zone!!!
    update_thermostat_response = ecobee_service.reset_preferences()
    logger.info(update_thermostat_response.pretty_format())
    assert update_thermostat_response.status.code == 0, 'Failure while executing reset_preferences:\n{0}'.format(
        update_thermostat_response.pretty_format())

Persistence
===========
The ecobee API specifies that all tokens issued must be stored by the application. These tokens represent the credentials of the user and must be kept secure. A simple way is to use the Python shelve module as follows

.. code-block:: python

    import shelve
    from datetime import datetime

    import pytz
    from six.moves import input

    from pyecobee import *


    def persist_to_shelf(file_name, ecobee_service):
        pyecobee_db = shelve.open(file_name, protocol=2)
        pyecobee_db[ecobee_service.thermostat_name] = ecobee_service
        pyecobee_db.close()


    def refresh_tokens(ecobee_service):
        token_response = ecobee_service.refresh_tokens()
        logger.debug('TokenResponse returned from ecobee_service.refresh_tokens():\n{0}'.format(
            token_response.pretty_format()))

        persist_to_shelf('pyecobee_db', ecobee_service)


    def request_tokens(ecobee_service):
        token_response = ecobee_service.request_tokens()
        logger.debug('TokenResponse returned from ecobee_service.request_tokens():\n{0}'.format(
            token_response.pretty_format()))

        persist_to_shelf('pyecobee_db', ecobee_service)


    def authorize(ecobee_service):
        authorize_response = ecobee_service.authorize()
        logger.debug('AutorizeResponse returned from ecobee_service.authorize():\n{0}'.format(
            authorize_response.pretty_format()))

        persist_to_shelf('pyecobee_db', ecobee_service)

        logger.info('Please goto ecobee.com, login to the web portal and click on the settings tab. Ensure the My '
                    'Apps widget is enabled. If it is not click on the My Apps option in the menu on the left. In the '
                    'My Apps widget paste "{0}" and in the textbox labelled "Enter your 4 digit pin to '
                    'install your third party app" and then click "Install App". The next screen will display any '
                    'permissions the app requires and will ask you to click "Authorize" to add the application.\n\n'
                    'After completing this step please hit "Enter" to continue.'.format(
            authorize_response.ecobee_pin))
        input()


    if __name__ == '__main__':
        thermostat_name = 'My Thermostat'
        try:
            pyecobee_db = shelve.open('pyecobee_db', protocol=2)
            ecobee_service = pyecobee_db[thermostat_name]
        except KeyError:
            application_key = input('Please enter the API key of your ecobee App: ')
            ecobee_service = EcobeeService(thermostat_name=thermostat_name, application_key=application_key)
        finally:
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
            token_response = ecobee_service.refresh_tokens()

        # Now make your requests :)


Tokens Refresh
==============
All access tokens must be refreshed periodically. Access tokens expire 3600 seconds (1 hour) from the time they were
refreshed. There are two patterns to refresh the access token.

Pro-active
----------
- Get the current date/time in UTC
- Compare the current date/time to the date/time on which the access and refresh token are due to expire
- Re-authorize app if the current date/time is later than the refresh token expiry date/time
- Refresh tokens if the current date/time is later than the access token expiry date/time

.. code-block:: python

        now_utc = datetime.now(pytz.utc)
        if now_utc > ecobee_service.refresh_token_expires_on:
            authorize(ecobee_service)
            request_tokens(ecobee_service)
        elif now_utc > ecobee_service.access_token_expires_on:
            token_response = ecobee_service.refresh_tokens()

Reactive
--------
The ecobee API returns status code 14 to indicate that a request was attempted using an expired access token. All
non-successful ecobee API responses are wrapped into the EcobeeApiException. The following code snippet demonstrates
how to refresh an expired access token

.. code-block:: python

        try:
            thermostat_summary_response = ecobee_service.request_thermostats_summary(selection=Selection(
            selection_type=SelectionType.REGISTERED.value,
            selection_match='',
            include_equipment_status=True))
        except EcobeeApiException as e:
            if e.status_code == 14:
                token_response = ecobee_service.refresh_tokens()

Date & Time Handling
====================
Some of the ecobee API requests expect the date and time to be in thermostat time, while others expect the date and time to be in UTC time.

Any EcobeeService method that accepts a datetime object as an argument expects the argument to be passed in thermostat time. The datetime object passed **must be a timezone aware** object.

.. code-block:: python

    import pytz
    from datetime import datetime

    from pytz import timezone

    eastern = timezone('US/Eastern')
    start_date_time=eastern.localize(datetime(2017, 5, 1, 10, 0, 0), is_dst=True) # 2017/05/01 10:00:00 -0400

The method will then either use the passed in datetime object as is, or convert it to its UTC time equivalent depending on the requirements of the ecobee API request being executed.

Exception Handling
==================
Your code should be prepared to handle the following Exceptions

- **EcobeeApiException**: Raised if a request results in an ecobee API error response
- **EcobeeAuthorizationException**: Raised if a request results in a standard or extended OAuth error response
- **EcobeeRequestsException**: Raised if a request results in an exception being raised by the underlying requests module
- **EcobeeHttpException**: Raised if a request results in any other HTTP error

Ecobee Exceptions Class Diagram
-------------------------------
.. image:: https://cdn.rawgit.com/sfanous/58a8e5b281b6e40035fb80b097154fc8/raw/a4eac7a59545ffd76414781b35afdf5d5fc07a2e/EcobeeExceptions.svg