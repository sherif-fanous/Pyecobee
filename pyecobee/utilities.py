import builtins
import inspect
import json
import keyword
import logging
import sys
import traceback

import requests
import six

from pyecobee.exceptions import EcobeeApiException
from pyecobee.exceptions import EcobeeAuthorizationException
from pyecobee.exceptions import EcobeeException
from pyecobee.exceptions import EcobeeHttpException
from pyecobee.exceptions import EcobeeRequestsException

# pylint: disable=unused-import
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

logger = logging.getLogger(__name__)


class Utilities(object):
    __slots__ = []

    _class_name_map = {'tou': 'TimeOfUse'}

    @classmethod
    def dictionary_to_object(
        cls,
        data,
        property_type,
        response_properties,
        parent_classes=[],
        indent=0,
        is_top_level=False,
    ):
        if isinstance(data, dict):
            for (i, key) in enumerate(data):
                if isinstance(data[key], dict):  # Object
                    # Append class of object to parent_classes
                    if len(parent_classes) > 1:
                        try:
                            parent_classes.append(
                                getattr(
                                    sys.modules[__name__],
                                    '{0}{1}'.format(key[:1].upper(), key[1:]),
                                )
                            )
                        except AttributeError:
                            parent_classes.append(
                                getattr(
                                    sys.modules[__name__],
                                    '{0}'.format(cls._class_name_map[key]),
                                )
                            )

                        # Nested object (i.e. This object is passed as
                        # an argument to its parent constructor
                        # (__init__) and must be passed as a keyword
                        # argument)
                        #
                        # This object is parent_classes[-1]
                        #
                        # This object's parent is parent_classes[-2]
                        generated_code = '{0}{1}={2}(\n'.format(
                            ' ' * indent,
                            parent_classes[-2].attribute_name_map[key],
                            parent_classes[-1].__name__,
                        )
                        response_properties[parent_classes[0]].append(generated_code)
                    else:
                        # Top level object
                        parent_classes = [key]
                        parent_classes.append(
                            getattr(
                                sys.modules[__name__],
                                '{0}{1}'.format(key[:1].upper(), key[1:]),
                            )
                        )

                        response_properties[parent_classes[0]] = []
                        generated_code = '{0}{1}(\n'.format(
                            ' ' * indent, parent_classes[-1].__name__
                        )
                        response_properties[parent_classes[0]].append(generated_code)

                    cls.dictionary_to_object(
                        data[key],
                        property_type,
                        response_properties,
                        parent_classes,
                        indent + 4,
                    )

                    generated_code = '{0})'.format(' ' * indent)
                    response_properties[parent_classes[0]].append(generated_code)

                    # The parent object's constructor will have a
                    # trailing ',' if its last argument is an object
                    generated_code = ',\n' if len(parent_classes) > 2 else '\n'
                    response_properties[parent_classes[0]].append(generated_code)

                    parent_classes.pop()
                elif isinstance(data[key], list):  # List
                    if len(parent_classes) > 1:
                        # Nested list (i.e. This list is passed as an
                        # argument to its parent constructor (__init__)
                        # and must be passed as a keyword argument)
                        generated_code = '{0}{1}=[\n'.format(
                            ' ' * indent, parent_classes[-1].attribute_name_map[key]
                        )
                        response_properties[parent_classes[0]].append(generated_code)
                    else:
                        # Top level list
                        parent_classes = [key]
                        response_properties[parent_classes[0]] = []

                        generated_code = '{0}[\n'.format(' ' * indent)
                        response_properties[parent_classes[0]].append(generated_code)

                    for (j, list_entry) in enumerate(data[key]):
                        parent_class_appended = False

                        if len(parent_classes) > 1:
                            # Get type of nested attribute (user defined
                            # object, list of user defined objects, or
                            # built-in data type)
                            class_name = parent_classes[-1].attribute_type_map[
                                parent_classes[-1].attribute_name_map[key]
                            ]

                            if class_name.find('List') != -1:
                                try:
                                    # Append class of user defined
                                    # object within list to
                                    # parent_classes (e.g. if attribute
                                    # type is List[Device], then append
                                    # Device to parent_classes
                                    parent_classes.append(
                                        getattr(sys.modules[__name__], class_name[5:-1])
                                    )
                                    parent_class_appended = True
                                except AttributeError:
                                    # No need to do any special handling
                                    # of built-in data types lists (e.g.
                                    # if attribute type is List[str],
                                    # the literal value is used
                                    pass
                        else:
                            # Top level list. Map the parent class from
                            # the property_type dictionary
                            parent_classes.append(property_type[key])
                            parent_class_appended = True

                        if parent_class_appended:
                            # De-serialize list of user defined objects
                            generated_code = '{0}{1}(\n'.format(
                                ' ' * (indent + 4), parent_classes[-1].__name__
                            )
                            response_properties[parent_classes[0]].append(
                                generated_code
                            )

                            cls.dictionary_to_object(
                                list_entry,
                                property_type,
                                response_properties,
                                parent_classes,
                                indent + 8,
                            )

                            parent_classes.pop()

                            generated_code = '{0})'.format(' ' * (indent + 4))
                            response_properties[parent_classes[0]].append(
                                generated_code
                            )
                        else:
                            # De-serialize user defined object or
                            # built-in data type
                            cls.dictionary_to_object(
                                list_entry,
                                property_type,
                                response_properties,
                                parent_classes,
                                indent + 4,
                            )

                        generated_code = ',\n' if j != len(data[key]) - 1 else '\n'
                        response_properties[parent_classes[0]].append(generated_code)

                    generated_code = '{0}]'.format(' ' * indent)
                    response_properties[parent_classes[0]].append(generated_code)

                    generated_code = ',\n' if i != len(data) - 1 else '\n'
                    response_properties[parent_classes[0]].append(generated_code)
                else:  # Object attributes
                    generated_code = ' ' * indent
                    response_properties[parent_classes[0]].append(generated_code)

                    if parent_classes:
                        try:
                            argument_name = parent_classes[-1].attribute_name_map[key]
                            if (
                                argument_name
                                in list(zip(*inspect.getmembers(builtins)))[0]
                                or argument_name in keyword.kwlist
                            ):
                                argument_name = '{0}_'.format(argument_name)

                            generated_code = '{0}={1!r}'.format(
                                argument_name, data[key]
                            )
                            response_properties[parent_classes[0]].append(
                                generated_code
                            )
                        except KeyError:
                            logger.error(
                                'Missing attribute in class %s\n'
                                'Attribute name  => %s\n'
                                'Attribute value => %s\n\n'
                                'Please open a new issue here '
                                '(https://github.com/sfanous/Pyecobee/issues/new)',
                                parent_classes[-1].__name__,
                                key,
                                data[key],
                            )
                    else:
                        generated_code = '{0}={1!r}'.format(key, data[key])
                        response_properties[parent_classes[0]].append(generated_code)

                    generated_code = ',\n' if i != len(data) - 1 else '\n'
                    response_properties[parent_classes[0]].append(generated_code)
        elif isinstance(data, list):
            generated_code = '{0}[\n'.format(' ' * indent)
            response_properties[parent_classes[0]].append(generated_code)

            for (i, list_entry) in enumerate(data):
                if i:
                    generated_code = ',\n'
                    response_properties[parent_classes[0]].append(generated_code)

                cls.dictionary_to_object(
                    list_entry,
                    property_type,
                    response_properties,
                    parent_classes,
                    indent + 4,
                )

            generated_code = '\n{0}]'.format(' ' * indent)
            response_properties[parent_classes[0]].append(generated_code)
        else:  # Built-in data type
            if isinstance(data, bool):
                generated_code = '{0}bool({1!r})'.format(' ' * indent, format(data))
            elif isinstance(data, int):
                generated_code = '{0}int({1!r})'.format(' ' * indent, format(data))
            else:
                generated_code = '{0}{1!r}'.format(' ' * indent, format(data))

            response_properties[parent_classes[0]].append(generated_code)

        if is_top_level:
            return eval(''.join(response_properties[parent_classes[0]]))

        return None

    @classmethod
    def make_http_request(
        cls, requests_http_method, url, headers=None, params=None, json_=None, timeout=5
    ):
        try:
            logger.debug(
                'Request\n'
                '[Method]\n'
                '========\n%s\n\n'
                '[URL]\n'
                '=====\n%s\n'
                '%s%s%s'.strip(),
                requests_http_method.__name__.upper(),
                url,
                '\n'
                '[Query Parameters]\n'
                '==================\n{0}\n'.format(
                    '\n'.join(
                        [
                            '{0:32} => {1!s}'.format(key, params[key])
                            for key in sorted(params)
                        ]
                    )
                )
                if params is not None
                else '',
                '\n'
                '[Headers]\n'
                '=========\n{0}\n'.format(
                    '\n'.join(
                        [
                            '{0:32} => {1!s}'.format(header, headers[header])
                            for header in sorted(headers)
                        ]
                    )
                )
                if headers is not None
                else '',
                '\n'
                '[JSON]\n'
                '======\n{0}\n'.format(json.dumps(json_, sort_keys=True, indent=2))
                if json_ is not None
                else '',
            )

            return requests_http_method(
                url, headers=headers, params=params, json=json_, timeout=timeout
            )
        except requests.exceptions.RequestException:
            (type_, value_, traceback_) = sys.exc_info()
            logger.error(
                '\n'.join(traceback.format_exception(type_, value_, traceback_))
            )

            six.reraise(EcobeeRequestsException, value_, traceback_)

    @classmethod
    def object_to_dictionary(cls, object_, class_):
        dictionary = {object_.__class__.__name__: {}}

        for attribute_name in object_.slots():
            attribute_value = getattr(object_, attribute_name)

            if attribute_value is not None:
                if isinstance(attribute_value, list):
                    dictionary[object_.__class__.__name__][
                        class_.attribute_name_map[attribute_name[1:]]
                    ] = []

                    for entry in attribute_value:
                        if hasattr(entry, '__slots__'):
                            dictionary[object_.__class__.__name__][
                                class_.attribute_name_map[attribute_name[1:]]
                            ].append(cls.object_to_dictionary(entry, type(entry)))
                        else:
                            dictionary[object_.__class__.__name__][
                                class_.attribute_name_map[attribute_name[1:]]
                            ].append(entry)
                else:
                    try:
                        getattr(sys.modules[__name__], type(attribute_value).__name__)

                        dictionary[object_.__class__.__name__][
                            class_.attribute_name_map[attribute_name[1:]]
                        ] = cls.object_to_dictionary(
                            attribute_value, type(attribute_value)
                        )
                    except AttributeError:
                        dictionary[object_.__class__.__name__][
                            class_.attribute_name_map[attribute_name[1:]]
                        ] = attribute_value

        return dictionary[object_.__class__.__name__]

    @classmethod
    def process_http_response(cls, response, response_class):
        if response.status_code == requests.codes.ok:
            response_object = cls.dictionary_to_object(
                {response_class.__name__: response.json()},
                {response_class.__name__: response_class},
                {response_class.__name__: None},
                is_top_level=True,
            )

            logger.debug(
                'EcobeeResponse:\n'
                '[JSON]\n'
                '======\n'
                '%s\n'
                '\n'
                '[Object]\n'
                '========\n'
                '%s'.strip(),
                json.dumps(response.json(), sort_keys=True, indent=2),
                response_object.pretty_format(),
            )

            return response_object

        try:
            if 'error' in response.json():
                error_response = cls.dictionary_to_object(
                    {'EcobeeErrorResponse': response.json()},
                    {'EcobeeErrorResponse': EcobeeErrorResponse},
                    {'EcobeeErrorResponse': None},
                    is_top_level=True,
                )

                raise EcobeeAuthorizationException(
                    'ecobee authorization error encountered for URL => {0}\n'
                    'HTTP error code => {1}\n'
                    'Error type => {2}\n'
                    'Error description => {3}\n'
                    'Error URI => {4}'.format(
                        response.request.url,
                        response.status_code,
                        error_response.error,
                        error_response.error_description,
                        error_response.error_uri,
                    ),
                    error_response.error,
                    error_response.error_description,
                    error_response.error_uri,
                )

            if 'status' in response.json():
                status = cls.dictionary_to_object(
                    {'Status': response.json()['status']},
                    {'Status': Status},
                    {'Status': None},
                    is_top_level=True,
                )

                raise EcobeeApiException(
                    'ecobee API error encountered for URL => {0}\n'
                    'HTTP error code => {1}\n'
                    'Status code => {2}\n'
                    'Status message => {3}'.format(
                        response.request.url,
                        response.status_code,
                        status.code,
                        status.message,
                    ),
                    status.code,
                    status.message,
                )

            raise EcobeeHttpException(
                'HTTP error encountered for URL => {0}\n'
                'HTTP error code => {1}'.format(
                    response.request.url, response.status_code
                )
            )
        except EcobeeException as ecobee_exception:
            logger.exception(
                '%s raised:\n', type(ecobee_exception).__name__, exc_info=True
            )

            raise
