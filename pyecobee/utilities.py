import sys

from .objects.action import Action
from .objects.alert import Alert
from .objects.climate import Climate
from .objects.demand_management import DemandManagement
from .objects.demand_response import DemandResponse
from .objects.device import Device
from .objects.electricity import Electricity
from .objects.electricity_device import ElectricityDevice
from .objects.electricity_tier import ElectricityTier
from .objects.equipment_setting import EquipmentSetting
from .objects.event import Event
from .objects.extended_runtime import ExtendedRuntime
from .objects.function import Function
from .objects.general_setting import GeneralSetting
from .objects.group import Group
from .objects.hierarchy_privilege import HierarchyPrivilege
from .objects.hierarchy_set import HierarchySet
from .objects.hierarchy_user import HierarchyUser
from .objects.house_details import HouseDetails
from .objects.limit_setting import LimitSetting
from .objects.location import Location
from .objects.management import Management
from .objects.meter_report import MeterReport
from .objects.meter_report_data import MeterReportData
from .objects.notification_settings import NotificationSettings
from .objects.output import Output
from .objects.page import Page
from .objects.program import Program
from .objects.remote_sensor import RemoteSensor
from .objects.remote_sensor_capability import RemoteSensorCapability
from .objects.report_job import ReportJob
from .objects.runtime import Runtime
from .objects.runtime_report import RuntimeReport
from .objects.runtime_sensor_metadata import RuntimeSensorMetadata
from .objects.runtime_sensor_report import RuntimeSensorReport
from .objects.security_settings import SecuritySettings
from .objects.selection import Selection
from .objects.sensor import Sensor
from .objects.settings import Settings
from .objects.state import State
from .objects.status import Status
from .objects.technician import Technician
from .objects.thermostat import Thermostat
from .objects.user import User
from .objects.utility import Utility
from .objects.version import Version
from .objects.weather import Weather
from .objects.weather_forecast import WeatherForecast
from .responses import EcobeeAuthorizeResponse
from .responses import EcobeeCreateRuntimeReportJobResponse
from .responses import EcobeeErrorResponse
from .responses import EcobeeGroupsResponse
from .responses import EcobeeIssueDemandResponsesResponse
from .responses import EcobeeListDemandResponsesResponse
from .responses import EcobeeListHierarchySetsResponse
from .responses import EcobeeListHierarchyUsersResponse
from .responses import EcobeeListRuntimeReportJobStatusResponse
from .responses import EcobeeMeterReportsResponse
from .responses import EcobeeRuntimeReportsResponse
from .responses import EcobeeStatusResponse
from .responses import EcobeeThermostatResponse
from .responses import EcobeeThermostatsSummaryResponse
from .responses import EcobeeTokensResponse


def dictionary_to_object(data, property_type, response_properties, parent_classes=[], indent=0, is_top_level=False):
    if isinstance(data, dict):
        for (i, key) in enumerate(data):
            if isinstance(data[key], dict):  # Object
                # Append class of object to parent_classes
                if len(parent_classes) > 1:
                    parent_classes.append(getattr(sys.modules[__name__], '{0}{1}'.format(key[:1].upper(), key[1:])))
                    # Nested object (i.e. This object is passed as an argument to its parent constructor (__init__)
                    # and  must be passed as a keyword argument)
                    # This object is parent_classes[-1]
                    # This object's parent is parent_classes[-2]
                    generated_code = '{0}{1}={2}(\n'.format(' ' * indent, parent_classes[-2].attribute_name_map[key],
                                                            parent_classes[-1].__name__)
                    response_properties[parent_classes[0]].append(generated_code)
                else:
                    # Top level object
                    parent_classes = [key]
                    parent_classes.append(getattr(sys.modules[__name__], '{0}{1}'.format(key[:1].upper(), key[1:])))
                    response_properties[parent_classes[0]] = []
                    generated_code = '{0}{1}(\n'.format(' ' * indent, parent_classes[-1].__name__)
                    response_properties[parent_classes[0]].append(generated_code)
                dictionary_to_object(data[key], property_type, response_properties, parent_classes, indent + 4)
                generated_code = '{0})'.format(' ' * indent)
                response_properties[parent_classes[0]].append(generated_code)

                # The parent object's constructor will have a trailing ',' if its last argument is an object
                generated_code = ',\n' if len(parent_classes) > 2 else '\n'
                response_properties[parent_classes[0]].append(generated_code)

                parent_classes.pop()
            elif isinstance(data[key], list):  # List
                if len(parent_classes) > 1:
                    # Nested list (i.e. This list is passed as an argument its parent constructor (__init__) and
                    # must be passed as a keyword argument)
                    generated_code = '{0}{1}=[\n'.format(' ' * indent, parent_classes[-1].attribute_name_map[key])
                    response_properties[parent_classes[0]].append(generated_code)
                else:
                    # Top level list
                    parent_classes = [key]
                    response_properties[parent_classes[0]] = []
                    # generated_code = '{0}{1}=[\n'.format(' ' * indent, key)
                    generated_code = '{0}[\n'.format(' ' * indent)
                    response_properties[parent_classes[0]].append(generated_code)

                for (j, list_entry) in enumerate(data[key]):
                    parent_class_appended = False
                    if len(parent_classes) > 1:
                        # Get type of nested attribute (user defined object, list of user defined objects, or built-in
                        # data type)
                        class_name = parent_classes[-1].attribute_type_map[parent_classes[-1].attribute_name_map[key]]
                        if class_name.find('List') != -1:
                            try:
                                # Append class of user defined object within list to parent_classes (e.g. if
                                # attribute type is List[Device], then append Device to parent_classes
                                parent_classes.append(getattr(sys.modules[__name__], class_name[5:-1]))
                                parent_class_appended = True
                            except AttributeError:
                                # No need to do any special handling of built-in data types lists (e.g. if attribute
                                # type is List[str], the literal value is used
                                pass
                    else:
                        # Top level list. Map the parent class from the property_type dictionary
                        parent_classes.append(property_type[key])
                        parent_class_appended = True

                    if parent_class_appended:
                        # De-serialize list of user defined objects
                        generated_code = '{0}{1}(\n'.format(' ' * (indent + 4), parent_classes[-1].__name__)
                        response_properties[parent_classes[0]].append(generated_code)
                        dictionary_to_object(list_entry, property_type, response_properties, parent_classes,
                                             indent + 8)
                        parent_classes.pop()
                        generated_code = '{0})'.format(' ' * (indent + 4))
                        response_properties[parent_classes[0]].append(generated_code)
                    else:
                        # De-serialize user defined object or built-in data type
                        dictionary_to_object(list_entry, property_type, response_properties, parent_classes,
                                             indent + 4)

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
                    generated_code = '{0}={1!r}'.format(parent_classes[-1].attribute_name_map[key], data[key])
                    response_properties[parent_classes[0]].append(generated_code)
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
            dictionary_to_object(list_entry, property_type, response_properties, parent_classes, indent + 4)
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


def object_to_dictionary(object_, class_):
    dictionary = {object_.__class__.__name__: {}}
    for attribute_name in object_.__slots__:
        attribute_value = getattr(object_, attribute_name)
        if attribute_value is not None:
            if isinstance(attribute_value, list):
                dictionary[object_.__class__.__name__][class_.attribute_name_map[attribute_name[1:]]] = []
                for entry in attribute_value:
                    if hasattr(entry, '__slots__'):
                        dictionary[object_.__class__.__name__][class_.attribute_name_map[attribute_name[1:]]].append(
                            object_to_dictionary(entry, type(entry)))
                    else:
                        dictionary[object_.__class__.__name__][class_.attribute_name_map[attribute_name[1:]]].append(
                            entry)
            else:
                try:
                    getattr(sys.modules[__name__], type(attribute_value).__name__)
                    dictionary[object_.__class__.__name__][class_.attribute_name_map[attribute_name[1:]]] = \
                        object_to_dictionary(attribute_value, type(attribute_value))
                except AttributeError:
                    dictionary[object_.__class__.__name__][
                        class_.attribute_name_map[attribute_name[1:]]] = attribute_value
    return dictionary[object_.__class__.__name__]
