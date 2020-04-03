import json
import logging
import numbers
import sys
import traceback
from datetime import date
from datetime import datetime
from datetime import timedelta

import pytz
import requests
import six

from . import utilities
from .ecobee_object import EcobeeObject
from .enumerations import AckType
from .enumerations import FanMode
from .enumerations import HoldType
from .enumerations import PlugState
from .enumerations import Scope
from .enumerations import SelectionType
from .exceptions import EcobeeApiException
from .exceptions import EcobeeAuthorizationException
from .exceptions import EcobeeException
from .exceptions import EcobeeHttpException
from .exceptions import EcobeeRequestsException
from .objects.demand_management import DemandManagement
from .objects.demand_response import DemandResponse
from .objects.function import Function
from .objects.group import Group
from .objects.hierarchy_privilege import HierarchyPrivilege
from .objects.hierarchy_user import HierarchyUser
from .objects.selection import Selection
from .objects.status import Status
from .objects.thermostat import Thermostat
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

logger = logging.getLogger(__name__)


class EcobeeService(EcobeeObject):
    __slots__ = ['_thermostat_name', '_application_key', '_authorization_token', '_access_token',
                 '_refresh_token', '_access_token_expires_on', '_refresh_token_expires_on', '_scope']

    AUTHORIZE_URL = 'https://api.ecobee.com/authorize'
    TOKENS_URL = 'https://api.ecobee.com/token'
    THERMOSTAT_SUMMARY_URL = 'https://api.ecobee.com/1/thermostatSummary'
    THERMOSTAT_URL = 'https://api.ecobee.com/1/thermostat'
    METER_REPORT_URL = 'https://api.ecobee.com/1/meterReport'
    RUNTIME_REPORT_URL = 'https://api.ecobee.com/1/runtimeReport'
    GROUP_URL = 'https://api.ecobee.com/1/group'
    HIERARCHY_SET_URL = 'https://api.ecobee.com/1/hierarchy/set'
    HIERARCHY_USER_URL = 'https://api.ecobee.com/1/hierarchy/user'
    HIERARCHY_THERMOSTAT_URL = 'https://api.ecobee.com/1/hierarchy/thermostat'
    DEMAND_RESPONSE_URL = 'https://api.ecobee.com/1/demandResponse'
    DEMAND_MANAGEMENT_URL = 'https://api.ecobee.com/1/demandManagement'
    RUNTIME_REPORT_JOB_URL = 'https://api.ecobee.com/1/runtimeReportJob'

    BEFORE_TIME_BEGAN_DATE_TIME = pytz.utc.localize(datetime(2008, 1, 2, 0, 0, 0))
    END_OF_TIME_DATE_TIME = pytz.utc.localize(datetime(2035, 1, 1, 0, 0, 0))

    MINIMUM_COOLING_TEMPERATURE = -10.0
    MAXIMUM_COOLING_TEMPERATURE = 120.0
    MINIMUM_HEATING_TEMPERATURE = 45.0
    MAXIMUM_HEATING_TEMPERATURE = 120.0

    attribute_name_map = {'thermostat_name': 'thermostat_name', 'application_key': 'application_key',
                          'authorization_token': 'authorization_token',
                          'access_token': 'access_token', 'refresh_token': 'refresh_token',
                          'access_token_expires_on': 'access_token_expires_on',
                          'refresh_token_expires_on': 'refresh_token_expires_on',
                          'scope': 'scope'}

    attribute_type_map = {'thermostat_name': 'six.text_type', 'application_key': 'six.text_type',
                          'authorization_token': 'six.text_type', 'access_token': 'six.text_type',
                          'refresh_token': 'six.text_type', 'access_token_expires_on': 'datetime',
                          'refresh_token_expires_on': 'datetime', 'scope': 'Scope'}

    def __init__(self,
                 thermostat_name,
                 application_key,
                 authorization_token=None,
                 access_token=None,
                 refresh_token=None,
                 access_token_expires_on=None,
                 refresh_token_expires_on=None,
                 scope=Scope.SMART_WRITE):
        """
        Construct an EcobeeService instance

        :param thermostat_name: Name of the thermostat
        :param application_key: The unique application key for your application
        :param authorization_token: Credentials to be used to retrieve the initial access_token and refresh_token
        :param access_token: Credentials to be used in all requests
        :param refresh_token: Credentials to be used to refresh access_token and refresh_token
        :param access_token_expires_on: When the access token expires on in UTC time
        :param refresh_token_expires_on: When the refresh token expires on in UTC time
        :param scope: Scope the application requests from the user. Valid values: Scope.SMART_READ,
        Scope.SMART_WRITE, and Scope.EMS
        """
        if not isinstance(application_key, six.string_types):
            raise TypeError('application_key must be an instance of {0}'.format(six.string_types))
        if len(application_key) != 32:
            raise ValueError('application_key must be a 32 alphanumeric string')

        self._thermostat_name = thermostat_name
        self._application_key = application_key
        self._authorization_token = authorization_token
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._access_token_expires_on = access_token_expires_on
        self._refresh_token_expires_on = refresh_token_expires_on
        self._scope = scope

    @staticmethod
    def __process_http_response(response, response_class):
        if response.status_code == requests.codes.ok:
            response_object = utilities.dictionary_to_object({response_class.__name__: response.json()},
                                                             {response_class.__name__: response_class},
                                                             {response_class.__name__: None},
                                                             is_top_level=True)
            if logger.getEffectiveLevel() >= logging.DEBUG:
                message_to_log = 'EcobeeResponse:\n' \
                                 '[JSON]\n' \
                                 '======\n' \
                                 '{0}\n' \
                                 '\n' \
                                 '[Object]\n' \
                                 '========\n' \
                                 '{1}'.format(json.dumps(response.json(), sort_keys=True, indent=2),
                                              response_object.pretty_format())
                logger.debug(message_to_log.strip())
            return response_object
        else:
            try:
                if 'error' in response.json():
                    error_response = utilities.dictionary_to_object({'EcobeeErrorResponse': response.json()},
                                                                    {'EcobeeErrorResponse': EcobeeErrorResponse},
                                                                    {'EcobeeErrorResponse': None},
                                                                    is_top_level=True)
                    raise EcobeeAuthorizationException('ecobee authorization error encountered for URL => {0}\n'
                                                       'HTTP error code => {1}\n'
                                                       'Error type => {2}\n'
                                                       'Error description => {3}\n'
                                                       'Error URI => {4}'.format(response.request.url,
                                                                                 response.status_code,
                                                                                 error_response.error,
                                                                                 error_response.error_description,
                                                                                 error_response.error_uri),
                                                       error_response.error,
                                                       error_response.error_description,
                                                       error_response.error_uri)
                elif 'status' in response.json():
                    status = utilities.dictionary_to_object({'Status': response.json()['status']},
                                                            {'Status': Status},
                                                            {'Status': None},
                                                            is_top_level=True)
                    raise EcobeeApiException('ecobee API error encountered for URL => {0}\n'
                                             'HTTP error code => {1}\n'
                                             'Status code => {2}\n'
                                             'Status message => {3}'.format(response.request.url,
                                                                            response.status_code,
                                                                            status.code,
                                                                            status.message),
                                             status.code,
                                             status.message)
                else:
                    raise EcobeeHttpException('HTTP error encountered for URL => {0}\n'
                                              'HTTP error code => {1}'.format(response.request.url,
                                                                              response.status_code))
            except EcobeeException as ecobee_exception:
                logger.exception('{0} raised:\n'.format(type(ecobee_exception).__name__), exc_info=True)
                raise

    @staticmethod
    def __make_http_request(requests_http_method, url, headers=None, params=None, json_=None, timeout=5):
        try:
            logger.debug('Request\n'
                         '[Method]\n'
                         '========\n{0}\n\n'
                         '[URL]\n'
                         '=====\n{1}\n'
                         '{2}{3}{4}'.format(requests_http_method.__name__.upper(),
                                            url,
                                            '\n'
                                            '[Query Parameters]\n'
                                            '==================\n{0}\n'.format('\n'.join(
                                                ['{0:32} => {1!s}'.format(key, params[key])
                                                 for key in sorted(params)])) if params is not None
                                            else '',
                                            '\n'
                                            '[Headers]\n'
                                            '=========\n{0}\n'.format(
                                                '\n'.join(
                                                    ['{0:32} => {1!s}'.format(header, headers[header])
                                                     for header in sorted(headers)])) if headers is not None
                                            else '',
                                            '\n'
                                            '[JSON]\n'
                                            '======\n{0}\n'.format(
                                                json.dumps(json_,
                                                           sort_keys=True,
                                                           indent=2)) if json_ is not None
                                            else '').strip())

            return requests_http_method(url,
                                        headers=headers,
                                        params=params,
                                        json=json_,
                                        timeout=timeout)
        except requests.exceptions.RequestException:
            (type_, value_, traceback_) = sys.exc_info()
            logger.error('\n'.join(traceback.format_exception(type_, value_, traceback_)))

            six.reraise(EcobeeRequestsException, value_, traceback_)

    def authorize(self, response_type='ecobeePin', timeout=5):
        """
        The authorize method allows a 3rd party application to obtain an authorization code and a 4 byte alphabetic
        string which can be displayed to the user. The user then logs into the ecobee Portal and registers the
        application using the PIN provided. Once this step is completed, the 3rd party application is able to
        request the access and refresh tokens using the request_tokens method.

        :param response_type: This is always "ecobeePin"
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An AuthorizeResponse object
        :rtype: EcobeeAuthorizeResponse
        :raises EcobeeAuthorizationException: If the request results in a standard or extended OAuth error
        response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If response_type is not a string
        :raises ValueError: If response_type is not set to "ecobeePin"
        """
        if not isinstance(response_type, six.string_types):
            raise TypeError('response_type must be an instance of {0}'.format(six.string_types))
        if response_type != 'ecobeePin':
            raise ValueError('response_type must be "ecobeePin"')

        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.AUTHORIZE_URL,
                                                     params={'client_id': self._application_key,
                                                             'response_type': response_type,
                                                             'scope': self._scope.value},
                                                     timeout=timeout)
        authorize_response = EcobeeService.__process_http_response(response, EcobeeAuthorizeResponse)
        self._authorization_token = authorize_response.code
        return authorize_response

    def request_tokens(self, grant_type='ecobeePin', timeout=5):
        """
        The request_tokens method is used to request the access and refresh tokens once the user has authorized the
        application within the ecobee Web Portal.

        :param grant_type: This is always "ecobeePin"
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A TokensResponse object
        :rtype: EcobeeTokensResponse
        :raises EcobeeAuthorizationException: If the request results in a standard or extended OAuth error
        response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If grant_type is not a string
        :raises ValueError: If grant_type is not set to "ecobeePin"
        """
        if not isinstance(grant_type, six.string_types):
            raise TypeError('grant_type must be an instance of {0}'.format(six.string_types))
        if grant_type != 'ecobeePin':
            raise ValueError('grant_type must be "ecobeePin"')

        now_utc = datetime.now(pytz.utc)
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.TOKENS_URL,
                                                     params={'client_id': self._application_key,
                                                             'code': self._authorization_token,
                                                             'grant_type': grant_type},
                                                     timeout=timeout)
        tokens_response = EcobeeService.__process_http_response(response, EcobeeTokensResponse)
        self._access_token = tokens_response.access_token
        self._access_token_expires_on = now_utc + timedelta(seconds=tokens_response.expires_in)
        self._refresh_token = tokens_response.refresh_token
        self._refresh_token_expires_on = now_utc + timedelta(days=365)
        return tokens_response

    def refresh_tokens(self, grant_type='refresh_token', timeout=5):
        """
        All access tokens must be refreshed periodically. Token refresh reduces the potential and benefit of token
        theft. Since all tokens expire, stolen tokens may only be used for a limited time. The refresh_tokens method
        immediately expires the previously issued access and refresh tokens and issues brand new tokens.

        :param grant_type: This is always "refresh_token"
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A TokensResponse object
        :rtype: EcobeeTokensResponse
        :raises EcobeeAuthorizationException: If the request results in a standard or extended OAuth error
        response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If grant_type is not a string
        :raises ValueError: If grant_type is not set to "refresh_token"
        """
        if not isinstance(grant_type, six.string_types):
            raise TypeError('grant_type must be an instance of {0}'.format(six.string_types))
        if grant_type != 'refresh_token':
            raise ValueError('grant_type must be "refresh_token"')

        now_utc = datetime.now(pytz.utc)
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.TOKENS_URL,
                                                     params={'client_id': self._application_key,
                                                             'code': self._refresh_token,
                                                             'grant_type': grant_type},
                                                     timeout=timeout)
        tokens_response = EcobeeService.__process_http_response(response, EcobeeTokensResponse)
        self._access_token = tokens_response.access_token
        self._access_token_expires_on = now_utc + timedelta(seconds=tokens_response.expires_in)
        self._refresh_token = tokens_response.refresh_token
        self._refresh_token_expires_on = now_utc + timedelta(days=365)
        return tokens_response

    def request_thermostats_summary(self, selection, timeout=5):
        """
        The request_thermostats_summary method retrieves a list of thermostat configuration and state
        revisions. This is a light-weight polling method which will only return the revision numbers for the
        significant portions of the thermostat data. It is the responsibility of the caller to store these revisions
        for future determination of whether changes occurred at the next poll interval.

        The intent is to permit the caller to determine whether a thermostat has changed since the last poll.
        Retrieval of a whole thermostat including runtime data is expensive and impractical for large amounts of
        thermostats such as a management set hierarchy, especially if nothing has changed. By storing the retrieved
        revisions, the caller may determine whether to get a thermostat and which sections of the thermostat should
        be retrieved.

        :param selection: The selection criteria for the request
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A ThermostatSummaryResponse object
        :rtype: EcobeeThermostatsSummaryResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection))}
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.THERMOSTAT_SUMMARY_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'json': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeThermostatsSummaryResponse)

    def request_thermostats(self, selection, timeout=5):
        """
        The request_thermostats method retrieves a selection of thermostat data for one or more thermostats. The type
        of data retrieved is determined by the selection argument. The include* attributes of the
        selection argument retrieve specific portions of the thermostat. When retrieving thermostats, request only
        the parts of the thermostat you require as the whole thermostat with everything can be quite large and
        generally unnecessary.

        :param selection: The selection criteria for the request
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A ThermostatResponse object
        :rtype: EcobeeThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection))}
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'json': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeThermostatResponse)

    def update_thermostats(self, selection, thermostat=None, functions=None, timeout=5):
        """
        The update_thermostats method permits the modification of any writable Thermostat or sub-object property.
        Thermostats may be updated by their writeable properties directly or through the Thermostat Functions.

        By including the Thermostat object in the request, any writable property may be directly updated in the
        thermostat. Some thermostat child objects are read-only due to either complexity in their configuration for
        which the thermostat functions have been created to support, or the object is not modifiable outside the
        physical thermostat (i.e. devices, wifi, etc.)

        Thermostats may also be updated using Thermostat Functions. Thermostat Functions provide a way to make more
        complex updates to a thermostat than just setting one or more properties. The functions emulate much of the
        same functionality found on the thermostat itself, such as setting a hold, for example. An update request may
        contain any number of functions in the request. Each function will be applied in the order they are listed in
        the request.

        :param selection: The selection criteria for the update
        :param thermostat: The thermostat object with properties to update
        :param functions: The list of functions to perform on all selected thermostats
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, thermostat is not an instance of Thermostat,
        functions is not a list, or any member of functions is not an instance of Function
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if thermostat is not None:
            if not isinstance(thermostat, Thermostat):
                raise TypeError('thermostat must be an instance of {0}'.format(Thermostat))
        if functions is not None:
            if not isinstance(functions, list):
                raise TypeError('functions must be an instance of {0}'.format(list))
        if functions is not None:
            for function_ in functions:
                if not isinstance(function_, Function):
                    raise TypeError('All members of functions must be a an instance of {0}'.format(Function))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection))}
        if thermostat:
            dictionary['thermostat'] = utilities.object_to_dictionary(thermostat, type(thermostat))
        if functions:
            dictionary['functions'] = [utilities.object_to_dictionary(function_, type(function_)) for function_ in
                                       functions]

        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def request_meter_reports(self, selection, start_date_time, end_date_time, meters='energy', timeout=5):
        """
        The request_meter_reports method retrieves the historical meter reading information for a selection of
        thermostats.

        The report request is limited to retrieving information for up to 25 thermostats with a maximum
        period of 31 days, per request. The amount of data returned is considerable for 31 days of data for 25
        thermostats (25 thermostats * 288 intervals per day * 31 days = 223,200 rows of data).

        The data in the report is at 5 minute intervals for a whole day. The data represented in terms of runtime
        is for the 5 minute interval (up to 300 seconds).

        :param selection: The selection criteria for the request. Must have selection_type = 'thermostats' and
        selection_match = A CSV string of thermostat identifiers.
        :param start_date_time: The start date and time in thermostat time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time. Must be a timezone aware datetime
        :param meters: A CSV string of meter types. Only supported meter type is "energy"
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A MeterReportResponse object
        :rtype: EcobeeMeterReportsResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, start_date_time is not a datetime,
        end_date_time is not a datetime, or meters is not a string
        :raises ValueError: If selection.selection_type is not thermostats, selection specifies more than 25
        thermostats, start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times are later
        than 2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, the duration
        between start_date_time and end_date_time is more than 31 days, meters is not a CSV string of "energy",
        or selection and meters don't have the same number of CSV entries
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if selection.selection_type != SelectionType.THERMOSTATS.value:
            raise ValueError('selection.selection_type must be set to {0}'.format(SelectionType.THERMOSTATS.value))
        if len(selection.selection_match.split(',')) > 25:
            raise ValueError('selection must not specify more than 25 thermostats')
        if not isinstance(start_date_time, datetime):
            raise TypeError('start_date must be an instance of {0}'.format(datetime))
        if start_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError('start_date must be later than {0}'.format(
                EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
            raise ValueError('start_date must be earlier than {0}'.format(
                EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if not isinstance(end_date_time, datetime):
            raise TypeError('end_date must be an instance of {0}'.format(datetime))
        if end_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError('end_date must be later than {0}'.format(
                EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if end_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
            raise ValueError('end_date must be earlier than {0}'.format(
                EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time >= end_date_time:
            raise ValueError('end_date_time must be later than start_date_time')
        if (end_date_time - start_date_time).days > 31:
            raise ValueError('Duration between start_date_time and end_date_time must not be more than 31 days')
        if not isinstance(meters, six.string_types):
            raise TypeError('meters must be an instance of {0}'.format(six.string_types))
        if not all(meter == 'energy' for meter in meters.split(',')):
            raise ValueError('meters must be a CSV string of "energy"')
        if len(selection.selection_match.split(',')) != len(meters.split(',')):
            raise ValueError('selection and meters must have the same number of CSV entries')

        utc = pytz.utc
        start_date_time = start_date_time.astimezone(utc)
        end_date_time = end_date_time.astimezone(utc)

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'startDate': '{0}-{1:02}-{2:02}'.format(start_date_time.year,
                                                              start_date_time.month,
                                                              start_date_time.day),
                      'startInterval': (start_date_time.hour * 12) + (start_date_time.minute // 5),
                      'endDate': '{0}-{1:02}-{2:02}'.format(end_date_time.year,
                                                            end_date_time.month,
                                                            end_date_time.day),
                      'endInterval': end_date_time.hour * 12 + (end_date_time.minute // 5),
                      'meters': meters
                      }
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.METER_REPORT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeMeterReportsResponse)

    def request_runtime_reports(self, selection, start_date_time, end_date_time, columns, include_sensors=False,
                                timeout=5):
        """
        The request_runtime_reports request is limited to retrieving information for up to 25 thermostats with a
        maximum period of 31 days, per request. The amount of data returned is considerable for 31 days of data for
        25 thermostats (25 thermostats * 288 intervals per day * 31 days = 223,200 rows of data).

        The data in the report is at 5 minute intervals for a whole day. The data represented in terms of runtime is
        for the 5 minute interval (up to 300 seconds).

        :param selection: The selection criteria for the request. Must have selection_type = 'thermostats' and
        selection_match = A CSV string of thermostat identifiers.
        :param start_date_time: The start date and time in thermostat time. Must be a timezone aware datetime.
        :param end_date_time: The end date and time in thermostat time. Must be a timezone aware datetime
        :param columns: A CSV string of column names
        :param include_sensors: Whether to include sensor runtime report data for those thermostats which have it.
        Default: False
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A RuntimeReportResponse object
        :rtype: EcobeeRuntimeReportsResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, start_date_time is not a datetime,
        end_date_time is not a datetime, columns is not a string, or include_sensors is not a boolean
        :raises ValueError: If selection.selection_type is not "thermostats", selection specifies more than 25
        thermostats, start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times are later
        than 2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, or the duration between
        start_date_time and end_date_time is more than 31 days
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if selection.selection_type != SelectionType.THERMOSTATS.value:
            raise ValueError('selection.selection_type must be set to {0}'.format(SelectionType.THERMOSTATS.value))
        if len(selection.selection_match.split(',')) > 25:
            raise ValueError('selection must not specify more than 25 thermostats')
        if not isinstance(start_date_time, datetime):
            raise TypeError('start_date must be an instance of {0}'.format(datetime))
        if start_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError('start_date must be later than {0}'.format(
                EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
            raise ValueError('start_date must be earlier than {0}'.format(
                EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if not isinstance(end_date_time, datetime):
            raise TypeError('end_date must be an instance of {0}'.format(datetime))
        if end_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError('end_date must be later than {0}'.format(
                EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if end_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
            raise ValueError('end_date must be earlier than {0}'.format(
                EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time >= end_date_time:
            raise ValueError('end_date_time must be later than start_date_time')
        if (end_date_time - start_date_time).days > 31:
            raise ValueError('Duration between start_date_time and end_date_time must not be more than 31 days')
        if not isinstance(columns, six.string_types):
            raise TypeError('columns must be an instance of {0}'.format(six.string_types))
        if not isinstance(include_sensors, bool):
            raise TypeError('include_sensors must be an instance of {0}'.format(bool))

        utc = pytz.utc
        start_date_time = start_date_time.astimezone(utc)
        end_date_time = end_date_time.astimezone(utc)

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'startDate': '{0}-{1:02}-{2:02}'.format(start_date_time.year, start_date_time.month,
                                                              start_date_time.day),
                      'startInterval': (start_date_time.hour * 12) + (start_date_time.minute // 5),
                      'endDate': '{0}-{1:02}-{2:02}'.format(end_date_time.year,
                                                            end_date_time.month,
                                                            end_date_time.day),
                      'endInterval': end_date_time.hour * 12 + (end_date_time.minute // 5),
                      'columns': columns,
                      'includeSensors': include_sensors
                      }
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.RUNTIME_REPORT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeRuntimeReportsResponse)

    def request_groups(self, selection, timeout=5):
        """
        The request_groups method retrieves the Group and grouping data for the Thermostats registered to the
        particular User. The User here refers to the calling application's user authorization.

        :param selection: The selection criteria for the request. Must have selection_type = 'registered'.
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A GroupResponse object
        :rtype: EcobeeGroupsResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        :raises ValueError: If selection.selection_type is not "registered"
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if selection.selection_type != SelectionType.REGISTERED.value:
            raise ValueError('selection.selection_type must be set to {0}'.format(SelectionType.REGISTERED.value))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection))}
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.GROUP_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeGroupsResponse)

    def update_groups(self, selection, groups, timeout=5):
        """
        The update_groups method permits the modification of any writable Group object properties.

        :param selection: The selection criteria for the request
        :param groups: The list of Groups to update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A GroupResponse object
        :rtype: EcobeeGroupsResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, groups is not a list, or any member of
        groups is not an instance of Group
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if not isinstance(groups, list):
            raise TypeError('groups must be an instance of {0}'.format(list))
        for group in groups:
            if not isinstance(group, Group):
                raise TypeError('All members of groups must be a an instance of {0}'.format(Group))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'groups': [utilities.object_to_dictionary(group, type(group)) for group in groups]}

        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.GROUP_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeGroupsResponse)

    def list_hierarchy_sets(self, set_path, recursive=False, include_privileges=False, include_thermostats=False,
                            timeout=5):
        """
        The list_hierarchy_sets method returns the management set hierarchy either at a single node depth and its
        children or recursively starting from the node path specified.

        :param set_path: The management set path
        :param recursive: Whether to also return the children of the children, recursively. Default: False
        :param include_privileges: Whether to include the privileges with each set. Default: False
        :param include_thermostats: Whether to include a list of all thermostat identifiers assigned to each set.
        Default: False
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A ListHierarchySetsResponse object
        :rtype: EcobeeListHierarchySetsResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, recursive is not a boolean, include_privileges is not a
        boolean, or include_thermostats is not a boolean
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(recursive, bool):
            raise TypeError('recursive must be an instance of {0}'.format(bool))
        if not isinstance(include_privileges, bool):
            raise TypeError('include_privileges must be an instance of {0}'.format(bool))
        if not isinstance(include_thermostats, bool):
            raise TypeError('include_thermostats must be an instance of {0}'.format(bool))

        dictionary = {'operation': 'list',
                      'setPath': set_path,
                      'recursive': recursive,
                      'includePrivileges': include_privileges,
                      'includeThermostats': include_thermostats}

        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.HIERARCHY_SET_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeListHierarchySetsResponse)

    def list_hierarchy_users(self, set_path, recursive=False, include_privileges=False, timeout=5):
        """
        The list_hierarchy_users method returns a list hierarchy users and privileges.

        :param set_path: The management set path
        :param recursive: Whether to also return the children of the children, recursively. Default: False
        :param include_privileges: Whether to include the privileges with each set. Default: False
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A ListHierarchyUsersResponse object
        :rtype: EcobeeListHierarchyUsersResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, recursive is not a boolean, of include_privileges is not a
        boolean
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(recursive, bool):
            raise TypeError('recursive must be an instance of {0}'.format(bool))
        if not isinstance(include_privileges, bool):
            raise TypeError('include_privileges must be an instance of {0}'.format(bool))

        dictionary = {'operation': 'list',
                      'setPath': set_path,
                      'recursive': recursive,
                      'includePrivileges': include_privileges}

        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.HIERARCHY_USER_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeListHierarchyUsersResponse)

    def add_hierarchy_set(self, set_name, parent_path, timeout=5):
        """
        The add_hierarchy_set adds a new set to the hierarchy.

        :param set_name: The name of the new set
        :param parent_path: The path to the parent for the new set
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, or parent_path is not a string
        """
        if not isinstance(set_name, six.string_types):
            raise TypeError('set_name must be an instance of {0}'.format(six.string_types))
        if not isinstance(parent_path, six.string_types):
            raise TypeError('parent_path must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'add',
                      'setName': set_name,
                      'parentPath': parent_path}

        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_SET_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def remove_hierarchy_set(self, set_path, timeout=5):
        """
        The remove_hierarchy_set method removes a set from the hierarchy.

        :param set_path: The path of the set to delete
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'remove',
                      'setPath': set_path}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_SET_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def rename_hierarchy_set(self, set_path, new_name, timeout=5):
        """
        The rename_hierarchy_set method renames a set in the hierarchy.

        :param set_path: The path of the set to rename
        :param new_name: The new name to assign. Must be unique to that parent
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, or new_name is not a string
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(new_name, six.string_types):
            raise TypeError('new_name must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'rename',
                      'setPath': set_path,
                      'newName': new_name}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_SET_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def move_hierarchy_set(self, set_path, to_path, timeout=5):
        """
        The move_hierarchy_set method moves a set to a new parent in the hierarchy. A parent may not be moved into
        its own child, nor can a set be moved into itself.

        :param set_path: The path of the set to move
        :param to_path: The path of the new parent to move to
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, or to_path is not a string
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(to_path, six.string_types):
            raise TypeError('to_path must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'move',
                      'setPath': set_path,
                      'toPath': to_path}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_SET_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def add_hierarchy_users(self, users, privileges=None, timeout=5):
        """
        The add_hierarchy_users method adds one or more new users to the hierarchy and optionally assigns privileges
        to the new users. The privileges being added must be only for the new users being added. If no privileges are
        provided, the user will be a member of the hierarchy but will not have access to any sets.

        When a new user is added, an invitation email is sent to the email provided as the userName property,
        which must be a valid email address. The user must then click on the invitation link to complete their
        registration.

        :param users: The list of users to add
        :param privileges: The privileges to assign to the new users
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If users is not a list, any member of users is not an instance of HierarchyUser,
        privileges is not a list, or any member of privileges is not an instance of HierarchyPrivilege
        """
        if not isinstance(users, list):
            raise TypeError('users must be an instance of {0}'.format(list))
        for user in users:
            if not isinstance(user, HierarchyUser):
                raise TypeError('All members of users must be a an instance of {0}'.format(HierarchyUser))
        if privileges is not None:
            if not isinstance(privileges, list):
                raise TypeError('privileges must be an instance of {0}'.format(list))
            for privilege in privileges:
                if not isinstance(privilege, HierarchyPrivilege):
                    raise TypeError('All members of privileges must be a an instance of {0}'.format(
                        HierarchyPrivilege))

        dictionary = {'operation': 'add',
                      'users': [utilities.object_to_dictionary(user, type(user)) for user in users]}
        if privileges:
            dictionary['privileges'] = [utilities.object_to_dictionary(privilege, type(privilege)) for privilege in
                                        privileges]
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_USER_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def remove_hierarchy_users(self, set_path, users, timeout=5):
        """
        The remove_hierarchy_users method removes one or more user privileges from a set. Only the privileges are
        removed from the specified set, the user remains in the hierarchy.

        :param set_path: The path to the set to remove user privileges from
        :param users: The users whose privileges to remove from the set
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, users is not a list, or any member of users is not an
        instance of HierarchyUser
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(users, list):
            raise TypeError('users must be an instance of {0}'.format(list))
        for user in users:
            if not isinstance(user, HierarchyUser):
                raise TypeError('All members of users must be a an instance of {0}'.format(HierarchyUser))

        dictionary = {'operation': 'remove',
                      'setPath': set_path,
                      'users': [utilities.object_to_dictionary(user, type(user)) for user in users]}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_USER_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def unregister_hierarchy_users(self, users, timeout=5):
        """
        The unregister_hierarchy_users method unregisters the user completely from the hierarchy and deletes the
        account. All set privileges are revoked.

        :param users: The users whose privileges to unregister
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If users is not a list, or any member of users is not an instance of HierarchyUser
        """
        if not isinstance(users, list):
            raise TypeError('users must be an instance of {0}'.format(list))
        for user in users:
            if not isinstance(user, HierarchyUser):
                raise TypeError('All members of users must be a an instance of {0}'.format(HierarchyUser))

        dictionary = {'operation': 'unregister',
                      'users': [utilities.object_to_dictionary(user, type(user)) for user in users]}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_USER_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def update_hierarchy_users(self, users=None, privileges=None, timeout=5):
        """
        The update_hierarchy_users method updates hierarchy user information and may update or add privileges to
        existing hierarchy users.

        :param users: The list of users to update
        :param privileges: The privileges to update or add
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If users is not a list, any member of users is not an instance of HierarchyUser,
        privileges is not a list, or any member of privileges is not an instance of HierarchyPrivilege
        :raises ValueError: If users is None and privileges is None
        """
        if users is not None:
            if not isinstance(users, list):
                raise TypeError('users must be an instance of {0}'.format(list))
            for user in users:
                if not isinstance(user, HierarchyUser):
                    raise TypeError('All members of users must be a an instance of {0}'.format(HierarchyUser))
        if privileges is not None:
            if not isinstance(privileges, list):
                raise TypeError('privileges must be an instance of {0}'.format(list))
            for privilege in privileges:
                if not isinstance(privilege, HierarchyPrivilege):
                    raise TypeError('All members of privileges must be a an instance of {0}'.format(
                        HierarchyPrivilege))
        if users is None and privileges is None:
            raise ValueError('Either users must not be None or privileges must not be None')

        dictionary = {'operation': 'update'}
        if users is not None:
            dictionary['users'] = [utilities.object_to_dictionary(user, type(user)) for user in users]
        if privileges is not None:
            dictionary['privileges'] = [utilities.object_to_dictionary(privilege, type(privilege)) for privilege in
                                        privileges]
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_USER_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def register_hierarchy_thermostats(self, thermostats, set_path=None, timeout=5):
        """
        The register_hierarchy_thermostats method registers one or more thermostats with the hierarchy and optionally
        assigns them to a hierarchy set.

        :param set_path: The set path to assign thermostat to
        :param thermostats: Comma separated list of thermostat identifiers to register
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If thermostats is not a string, or set_path is not a string
        """
        if not isinstance(thermostats, six.string_types):
            raise TypeError('thermostats must be an instance of {0}'.format(six.string_types))
        if set_path is not None:
            if not isinstance(set_path, six.string_types):
                raise TypeError('set_path must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'register',
                      'thermostats': thermostats}
        if set_path is not None:
            dictionary['setPath'] = set_path
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def unregister_hierarchy_thermostats(self, thermostats, timeout=5):
        """
        The unregister_hierarchy_thermostats method unregisters one or more thermostat from the hierarchy. The
        thermostat is completely disassociated from the hierarchy.

        :param thermostats: Comma separated list of thermostat identifiers to unregister
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If thermostats is not a string
        """
        if not isinstance(thermostats, six.string_types):
            raise TypeError('thermostats must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'unregister',
                      'thermostats': thermostats}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def move_hierarchy_thermostats(self, set_path, to_path, thermostats=None, timeout=5):
        """
        The move_hierarchy_thermostats method moves thermostats between hierarchy sets. A thermostat may only reside
        inside a single set. Users may be moved in and out of the Unassigned set.
        :param set_path: The set path the thermostats are being moved from
        :param to_path: The set path the thermostats are being moved to
        :param thermostats: Comma separated list of thermostat identifiers to move. If this argument is None, all
        thermostats which reside in the set_path will be moved
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, to_path is not a string, or thermostats is not a string
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(to_path, six.string_types):
            raise TypeError('to_path must be an instance of {0}'.format(six.string_types))
        if thermostats is not None:
            if not isinstance(thermostats, six.string_types):
                raise TypeError('thermostats must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'move',
                      'setPath': set_path,
                      'toPath': to_path}
        if thermostats is not None:
            dictionary['thermostats'] = thermostats
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def assign_hierarchy_thermostats(self, set_path, thermostats, timeout=5):
        """
        The assign_hierarchy_thermostats method forcefully moves one or more thermostats from their current set to
        the specified set. At the end of the successful operation the thermostat(s) will be in the specified set.

        :param set_path: The set path the thermostats are being moved to
        :param thermostats: Comma separated list of thermostat identifiers to assign
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If set_path is not a string, or thermostats is not a string
        """
        if not isinstance(set_path, six.string_types):
            raise TypeError('set_path must be an instance of {0}'.format(six.string_types))
        if not isinstance(thermostats, six.string_types):
            raise TypeError('thermostats must be an instance of {0}'.format(six.string_types))

        dictionary = {'operation': 'assign',
                      'setPath': set_path,
                      'thermostats': thermostats}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.HIERARCHY_THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def list_demand_responses(self, timeout=5):
        """
        The list_demand_responses method returns a list of all demand response event which have been issued and have
        not yet expired.

        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A ListDemandResponses object
        :rtype: EcobeeListDemandResponsesResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        """
        dictionary = {'operation': 'list'}
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.DEMAND_RESPONSE_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeListDemandResponsesResponse)

    def issue_demand_response(self, selection, demand_response, timeout=5):
        """
        The issue_demand_response method creates a demand response event. Demand EcobeeResponse events may be issued to 
        a set of thermostats in order to adjust their program. Demand EcobeeResponse events are either optional or 
        mandatory. Mandatory events may not be cancelled by the user and must run their course.

        :param selection: The selection criteria for update
        :param demand_response: The demand response object to create
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, or demand_response is not an instance of
        DemandResponse
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if not isinstance(demand_response, DemandResponse):
            raise TypeError('demand_response must be an instance of {0}'.format(DemandResponse))
        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'operation': 'create',
                      'demandResponse': utilities.object_to_dictionary(demand_response, type(demand_response))}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.DEMAND_RESPONSE_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeIssueDemandResponsesResponse)

    def cancel_demand_response(self, demand_response_ref, timeout=5):
        """
        The cancel_demand_response method cancels a scheduled demand response event. When cancelled, the demand
        response event will be removed from all thermostats in the selection.

        :param demand_response_ref: The system generated ID of the demand response to cancel
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If demand_response_ref is not a string
        """
        if not isinstance(demand_response_ref, six.text_type):
            raise TypeError('demand_response_ref must be an instance of {0}'.format(six.text_type))
        dictionary = {'operation': 'cancel', 'demandResponse': {'demandResponseRef': demand_response_ref}}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.DEMAND_RESPONSE_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def issue_demand_managements(self, selection, demand_managements, timeout=5):
        """
        The issue_demand_managements method creates demand management objects that permit a Utility to forecast and
        adjust the thermostat runtime dynamically with a 5 minute granularity per adjustment. Each DM object defines
        a single hour of a day with its 12 5-minute intervals which specify the temperature adjustment . The
        thermostat will apply this temperature adjustment on top of the user's program.

        :param selection: The selection criteria for update
        :param demand_managements: A list of demand management objects
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, demand_managements is not a list,
        or any member of privileges is not an instance of DemandManagement
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if not isinstance(demand_managements, list):
            raise TypeError('demand_managements must be an instance of {0}'.format(list))
        for demand_management in demand_managements:
            if not isinstance(demand_management, DemandManagement):
                raise TypeError('All members of demand_managements must be a an instance of {0}'.format(
                    DemandManagement))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'dmList': [utilities.object_to_dictionary(demand_management, type(demand_management)) for
                                 demand_management in demand_managements]}
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.DEMAND_MANAGEMENT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def create_runtime_report_job(self, selection, start_date, end_date, columns, include_sensors=False, timeout=5):
        """

        :param selection: The selection criteria for the request. Must have selection_type = 'thermostats' or
        'managementSet'
        :param start_date: The report start date
        :param end_date: The report end date
        :param columns: A CSV string of column names
        :param include_sensors: Whether to include sensor runtime report data for those thermostats which have it.
        Default: False
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A CreateRuntimeReportResponse object
        :rtype: EcobeeCreateRuntimeReportJobResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection, start_date is not a date, end_date is not a
        date, columns is not a string, or include_sensors is not a boolean
        :raises ValueError: If start/end date are earlier than 2008-01-02, start/end date_times are later than
        2035-01-01, or start_date is later than end_date
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))
        if selection.selection_type != SelectionType.MANAGEMENT_SET.value and selection.selection_type != \
                SelectionType.THERMOSTATS.value:
            raise ValueError('selection.selection_type must be set to {0} or {1}'.format(
                SelectionType.MANAGEMENT_SET.value, SelectionType.THERMOSTATS.value))
        if not isinstance(start_date, date):
            raise TypeError('start_date must be an instance of {0}'.format(date))
        if pytz.utc.localize(datetime(start_date.year, start_date.month, start_date.day, 0, 0,
                                      0)) < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError('start_date must be later than {0}'.format(
                EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if pytz.utc.localize(datetime(start_date.year, start_date.month, start_date.day, 0, 0,
                                      0)) > EcobeeService.END_OF_TIME_DATE_TIME:
            raise ValueError('start_date must be earlier than {0}'.format(
                EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if not isinstance(end_date, date):
            raise TypeError('end_date must be an instance of {0}'.format(date))
        if pytz.utc.localize(datetime(end_date.year, end_date.month, end_date.day, 0, 0,
                                      0)) < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
            raise ValueError('end_date must be later than {0}'.format(
                EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if pytz.utc.localize(datetime(end_date.year, end_date.month, end_date.day, 0, 0,
                                      0)) > EcobeeService.END_OF_TIME_DATE_TIME:
            raise ValueError('end_date must be earlier than {0}'.format(
                EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date >= end_date:
            raise ValueError('end_date must be later than start_date')
        if not isinstance(columns, six.text_type):
            raise TypeError('columns must be an instance of {0}'.format(six.text_type))
        if not isinstance(include_sensors, bool):
            raise TypeError('include_sensors must be an instance of {0}'.format(bool))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'startDate': '{0}-{1:02}-{2:02}'.format(start_date.year, start_date.month, start_date.day),
                      'endDate': '{0}-{1:02}-{2:02}'.format(end_date.year, end_date.month, end_date.day),
                      'columns': columns,
                      'includeSensors': include_sensors}
        response = EcobeeService.__make_http_request(requests.post,
                                                     '{0}/create'.format(EcobeeService.RUNTIME_REPORT_JOB_URL),
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeCreateRuntimeReportJobResponse)

    def list_runtime_report_job_status(self, job_id=None, timeout=5):
        """
        The list_runtime_report_job_status method gets the status of the job for the given id or all current job
        statuses for the account carrying out the request.

        :param job_id: The id of the report job to get the status
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A ListRuntimeReportJobStatusResponse object
        :rtype: EcobeeListRuntimeReportJobStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If job_id is not a string
        """
        if job_id is not None:
            if not isinstance(job_id, six.text_type):
                raise TypeError('job_id must be an instance of {0}'.format(six.text_type))

        dictionary = {}
        if job_id:
            dictionary['jobId'] = job_id
        response = EcobeeService.__make_http_request(requests.post,
                                                     '{0}/status'.format(EcobeeService.RUNTIME_REPORT_JOB_URL),
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json',
                                                             'body': json.dumps(dictionary, sort_keys=True, indent=2)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeListRuntimeReportJobStatusResponse)

    def cancel_runtime_report_job(self, job_id, timeout=5):
        """
        The cancel_runtime_report_job method cancels any queued report job to avoid getting processed and to allow
        for queuing additional report jobs. A job that is already being processed will be completed,
        even if a request has been made to cancel it.

        :param job_id: The id of the report job to cancel
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A StatusResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If job_id is not a string
        """
        if not isinstance(job_id, six.text_type):
            raise TypeError('job_id must be an instance of {0}'.format(six.text_type))

        dictionary = {'jobId': job_id}
        response = EcobeeService.__make_http_request(requests.post,
                                                     '{0}/cancel'.format(EcobeeService.RUNTIME_REPORT_JOB_URL),
                                                     headers={'Authorization': 'Bearer {0}'.format(
                                                         self._access_token),
                                                              'Content-Type': 'application/json;charset=UTF-8'},
                                                     params={'format': 'json'},
                                                     json_=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, EcobeeStatusResponse)

    def acknowledge(self,
                    thermostat_identifier,
                    ack_ref,
                    ack_type,
                    remind_me_later=False,
                    selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                    timeout=5):
        """
        The acknowledge method allows an alert to be acknowledged.

        :param thermostat_identifier: The thermostat identifier to acknowledge the alert for
        :param ack_ref: The acknowledge ref of alert
        :param ack_type: The type of acknowledgement. Valid values: accept, decline, defer, unacknowledged
        :param remind_me_later: Whether to remind at a later date, if this is a defer acknowledgement
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If thermostat_identifier is not a string, ack_ref is not a string, ack_type is not a
        member of AckType, remind_me_later is not a boolean, or selection is not an instance of Selection
        """
        if not isinstance(thermostat_identifier, six.string_types):
            raise TypeError('thermostat_identifier must be an instance of {0}'.format(six.string_types))
        if not isinstance(ack_ref, six.string_types):
            raise TypeError('ack_ref must be an instance of {0}'.format(six.string_types))
        if not isinstance(ack_type, AckType):
            raise TypeError('ack_type must be an instance of {0}'.format(AckType))
        if not isinstance(remind_me_later, bool):
            raise TypeError('remind_me_later must be an instance of {0}'.format(bool))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='acknowledge',
                                                           params={'thermostatIdentifier': thermostat_identifier,
                                                                   'ackRef': ack_ref,
                                                                   'ackType': ack_type.value,
                                                                   'remindMeLater': remind_me_later})],
                                       timeout=timeout)

    def control_plug(self,
                     plug_name,
                     plug_state,
                     start_date_time=None,
                     end_date_time=None,
                     hold_type=HoldType.INDEFINITE,
                     hold_hours=None,
                     selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                     timeout=5):
        """
        The control_plug method controls the on/off state of a plug by setting a hold on the plug, creating a hold for
        the on or off state of the plug for the specified duration.

        Note that an event is created regardless of whether the program is in the same state as the requested state.

        :param plug_name: The name of the plug. Ensure each plug has a unique name
        :param plug_state: The state to put the plug into. Valid values: PlugState.ON, PlugState.OFF, PlugState.RESUME
        :param start_date_time: The start date and time in thermostat time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time. Must be a timezone aware datetime
        :param hold_type: The hold duration type. Valid values: HoldType.DATE_TIME, HoldType.NEXT_TRANSITION,
        HoldType.INDEFINITE, and HoldType.HOLD_HOURS
        :param hold_hours: The number of hours to hold for, used and required if holdType='holdHours'
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If plug_name is not a string, plug_state is not a member of PlugState, start_date_time is
        not a datetime, end_date_time is not a datetime, hold_type is not a member of HoldType, hold_hours is not an
        integer, or selection is not an instance of Selection
        :raises ValueError: If start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times
        are later than 2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, end_date_time is None
        while hold_type is HoldType.DATE_TIME, or hold_hours is None while hold_type is HoldType.HOLD_HOURS
        """
        if not isinstance(plug_name, six.string_types):
            raise TypeError('plug_name must be an instance of {0}'.format(six.string_types))
        if not isinstance(plug_state, PlugState):
            raise TypeError('plug_state must be an instance of {0}'.format(PlugState))
        if start_date_time is not None:
            if not isinstance(start_date_time, datetime):
                raise TypeError('start_date_time must be an instance of {0}'.format(datetime))
            if start_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('start_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if start_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('start_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if end_date_time is not None:
            if not isinstance(end_date_time, datetime):
                raise TypeError('end_date_time must be an instance of {0}'.format(datetime))
            if end_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('end_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if end_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('end_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time is not None and end_date_time is not None and start_date_time >= end_date_time:
            raise ValueError('end_date_time must be later than start_date_time')
        if not isinstance(hold_type, HoldType):
            raise TypeError('hold_type must be an instance of {0}'.format(HoldType))
        if hold_type == HoldType.DATE_TIME and end_date_time is None:
            raise ValueError('hold_type is {0}. end_date_time must not be None'.format(HoldType.DATE_TIME.value))
        if hold_hours is not None and not isinstance(hold_hours, int):
            raise TypeError('hold_hours must be an instance of {0}'.format(int))
        if hold_type == HoldType.HOLD_HOURS and hold_hours is None:
            raise ValueError('hold_type is {0}. hold_hours must not be None'.format(HoldType.HOLD_HOURS.value))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        control_plug_parameters = {'plugName': plug_name, 'plugState': plug_state.value, 'holdType': hold_type.value}
        if start_date_time:
            control_plug_parameters['startDate'] = '{0}-{1:02}-{2:02}'.format(start_date_time.year,
                                                                              start_date_time.month,
                                                                              start_date_time.day)
            control_plug_parameters['startTime'] = '{0:02}:{1:02}:{2:02}'.format(start_date_time.hour,
                                                                                 start_date_time.minute,
                                                                                 start_date_time.second)
        if end_date_time:
            control_plug_parameters['endDate'] = '{0}-{1:02}-{2:02}'.format(end_date_time.year, end_date_time.month,
                                                                            end_date_time.day)
            control_plug_parameters['endTime'] = '{0:02}:{1:02}:{2:02}'.format(end_date_time.hour,
                                                                               end_date_time.minute,
                                                                               end_date_time.second)
        if hold_hours:
            control_plug_parameters['holdHours'] = hold_hours

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='controlPlug',
                                                           params=control_plug_parameters)],
                                       timeout=timeout)

    def create_vacation(self,
                        name,
                        cool_hold_temp,
                        heat_hold_temp,
                        start_date_time=None,
                        end_date_time=None,
                        fan_mode=FanMode.AUTO,
                        fan_min_on_time=0,
                        selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                        timeout=5):
        """
        The create_vacation method creates a vacation event on the thermostat. If the start/end date_times are not
        provided for the vacation event, the vacation event will begin immediately and last 14 days.

        If both the cool_hold_temp and heat_hold_temp arguments provided to this method have the same value,
        and the Thermostat is in auto mode, then the two values will be adjusted during processing to be separated by
        the value stored in Thermostat.Settings.heatCoolMinDelta.

        :param name: The vacation event name. It must be unique
        :param cool_hold_temp: The temperature in Fahrenheit to set the cool vacation hold at
        :param heat_hold_temp: The temperature in Fahrenheit to set the heat vacation hold at
        :param start_date_time: The start date and time in thermostat time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time. Must be a timezone aware datetime
        :param fan_mode: The fan mode during the vacation. Values: auto, on. Default: auto
        :param fan_min_on_time: The minimum number of minutes to run the fan each hour. Range: 0-60. Default: 0
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If name is not a string, cool_hold_temp is not a real number, heat_hold_temp is not a real
        number, start_date_time is not a datetime, end_date_time is not a datetime, fan_mode is not a member of FanMode,
        fan_min_on_time is not an integer, or selection is not an instance of Selection
        :raises ValueError: If cool_hold_temp is lower than -10F, cool_hold_temp is higher than 120F,
        heat_hold_temp is lower than 45F, heat_hold_temp is higher than 120F, start/end date_times are earlier than
        2008-01-02 00:00:00 +0000, start/end date_times are later than 2035-01-01 00:00:00 +0000, start_date_time is
        later than end_date_time, or fan_min_on_time is less than 0 or greater than 60
        """
        if not isinstance(name, six.string_types):
            raise TypeError('name must be an instance of {0}'.format(six.string_types))
        if not isinstance(cool_hold_temp, numbers.Real):
            raise TypeError('cool_hold_temp must be an instance of {0}'.format(numbers.Real))
        if not (EcobeeService.MINIMUM_COOLING_TEMPERATURE <= float(cool_hold_temp) <=
                EcobeeService.MAXIMUM_COOLING_TEMPERATURE):
            raise ValueError('cool_hold_temp must be between {0}F and {1}F'.format(
                EcobeeService.MINIMUM_COOLING_TEMPERATURE, EcobeeService.MAXIMUM_COOLING_TEMPERATURE))
        if not isinstance(heat_hold_temp, numbers.Real):
            raise TypeError('heat_hold_temp must be an instance of {0}'.format(numbers.Real))
        if not (EcobeeService.MINIMUM_HEATING_TEMPERATURE <= float(heat_hold_temp) <=
                EcobeeService.MAXIMUM_HEATING_TEMPERATURE):
            raise ValueError('heat_hold_temp must be between {0}F and {1}F'.format(
                EcobeeService.MINIMUM_HEATING_TEMPERATURE, EcobeeService.MAXIMUM_HEATING_TEMPERATURE))
        if start_date_time is not None:
            if not isinstance(start_date_time, datetime):
                raise TypeError('start_date_time must be an instance of {0}'.format(datetime))
            if start_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('start_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if start_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('start_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if end_date_time is not None:
            if not isinstance(end_date_time, datetime):
                raise TypeError('end_date_time must be an instance of {0}'.format(datetime))
            if end_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('end_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if end_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('end_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time is not None and end_date_time is not None and start_date_time >= end_date_time:
            raise ValueError('end_date_time must be later than start_date_time')
        if not isinstance(fan_mode, FanMode):
            raise TypeError('fan_mode must be an instance of {0}'.format(FanMode))
        if not isinstance(fan_min_on_time, int):
            raise TypeError('fan_min_on_time must be an instance of {0}'.format(int))
        if fan_min_on_time not in range(0, 61):
            raise ValueError('fan_min_on_time must be between 0 and 60')
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        create_vacation_parameters = {'name': name, 'coolHoldTemp': int(cool_hold_temp * 10),
                                      'heatHoldTemp': int(heat_hold_temp * 10), 'fan': fan_mode.value,
                                      'fanMinOnTime': str(fan_min_on_time)}
        if start_date_time:
            create_vacation_parameters['startDate'] = '{0}-{1:02}-{2:02}'.format(start_date_time.year,
                                                                                 start_date_time.month,
                                                                                 start_date_time.day)
            create_vacation_parameters['startTime'] = '{0:02}:{1:02}:{2:02}'.format(start_date_time.hour,
                                                                                    start_date_time.minute,
                                                                                    start_date_time.second)
        if end_date_time:
            create_vacation_parameters['endDate'] = '{0}-{1:02}-{2:02}'.format(end_date_time.year,
                                                                               end_date_time.month,
                                                                               end_date_time.day)
            create_vacation_parameters['endTime'] = '{0:02}:{1:02}:{2:02}'.format(end_date_time.hour,
                                                                                  end_date_time.minute,
                                                                                  end_date_time.second)

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='createVacation',
                                                           params=create_vacation_parameters)],
                                       timeout=timeout)

    def delete_vacation(self,
                        name,
                        selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                        timeout=5):
        """
        The delete_vacation method deletes a vacation event from a thermostat. This is the only way to cancel a
        vacation event. This method is able to remove vacation events not yet started and scheduled in the future.

        :param name: The vacation event name to delete
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If name is not a string, or selection is not an instance of Selection
        """
        if not isinstance(name, six.string_types):
            raise TypeError('name must be an instance of {0}'.format(six.string_types))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='deleteVacation',
                                                           params={'name': name})],
                                       timeout=timeout)

    def reset_preferences(self,
                          selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                          timeout=5):
        """
        The reset_preferences method sets all of the user configurable settings back to the factory default values.
        This method call will not only reset the top level thermostat settings such as hvacMode, lastServiceDate and
        vent, but also all of the user configurable fields of the Thermostat.Settings and Thermostat.Program objects.

        Note that this does not reset all values. For example, the installer settings and wifi details remain untouched.

        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='resetPreferences')],
                                       timeout=timeout)

    def resume_program(self,
                       resume_all=False,
                       selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                       timeout=5):
        """
        The resume_program method removes the currently running event providing the event is not a mandatory demand
        response event. If the resume_all argument is set to False, the top active event is removed from the stack and
        the thermostat resumes its program or enters the next event in the stack if one exists. If the resume_all
        argument is set to True, the method resumes all events and returns the thermostat to its program.

        :param resume_all: Should the thermostat be resumed to the next event (False) or to it's program (True)
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If resume_all is not a boolean, or selection is not an instance of Selection
        """
        if not isinstance(resume_all, bool):
            raise TypeError('resume_all must be an instance of {0}'.format(bool))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='resumeProgram',
                                                           params={'resumeAll': resume_all})],
                                       timeout=timeout)

    def send_message(self,
                     text,
                     selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                     timeout=5):
        """
        The send_message method allows an alert message to be sent to the thermostat. The message properties are
        same as those of the Alert Object.

        :param text: The message text to send. Text will be truncated to 500 characters if longer
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If text is not a string, or selection is not an instance of Selection
        """
        if not isinstance(text, six.string_types):
            raise TypeError('text must be an instance of {0}'.format(six.string_types))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='sendMessage',
                                                           params={'text': text})],
                                       timeout=timeout)

    def set_hold(self,
                 cool_hold_temp,
                 heat_hold_temp,
                 hold_climate_ref=None,
                 start_date_time=None,
                 end_date_time=None,
                 hold_type=HoldType.INDEFINITE,
                 hold_hours=None,
                 selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                 timeout=5):
        """
        The set_hold method sets the thermostat into a hold with the specified temperature creating a hold for the
        specified duration. Note that an event is created regardless of whether the program is in the same state as
        the requested state.

        There is also support for creating a hold by passing a hold_climate_ref argument to this method. When an
        existing and valid Climate.climate_ref value is passed to this method, the cool_hold_temp, heat_hold_temp and
        fan mode from that Climate are used in the creation of the hold event. The values from that Climate will take
        precedence over any cool_hold_temp, heat_hold_temp and fan mode parameters passed into this method separately.

        :param cool_hold_temp: The temperature in Fahrenheit to set the cool vacation hold at
        :param heat_hold_temp: The temperature in Fahrenheit to set the heat vacation hold at
        :param hold_climate_ref: The Climate to use as reference for setting the cool_hold_temp, heat_hold_temp and fan
        settings for this hold. If this value is passed the cool_hold_temp and heat_hold_temp are not required
        :param start_date_time: The start date and time in thermostat time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time. Must be a timezone aware datetime
        :param hold_type: The hold duration type. Valid values: HoldType.DATE_TIME, HoldType.NEXT_TRANSITION,
        HoldType.INDEFINITE, and HoldType.HOLD_HOURS
        :param hold_hours: The number of hours to hold for, used and required if holdType='holdHours'
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If cool_hold_temp is not a real, heat_hold_temp is not a real, hold_climate_ref is not a
        string, start_date_time is not a datetime, end_date_time is not a datetime, hold_type is not a member
        of HoldType, hold_hours is not an integer, or selection is not an instance of Selection
        :raises ValueError: If cool_hold_temp is lower than -10F, cool_hold_temp is higher than 120F,
        heat_hold_temp is lower than 45F, heat_hold_temp is higher than 120F, cool_hold_temp, heat_hold_temp,
        and hold_climate_ref are None, hold_climate_ref is None and either cool_hold_temp or heat_hold_temp are None,
        start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times are later than
        2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, end_date_time is None while hold_type
        is HoldType.DATE_TIME, or hold_hours is None while hold_type is HoldType.HOLD_HOURS
        """
        if cool_hold_temp is not None:
            if not isinstance(cool_hold_temp, numbers.Real):
                raise TypeError('cool_hold_temp must be an instance of {0}'.format(numbers.Real))
            if not (EcobeeService.MINIMUM_COOLING_TEMPERATURE <= float(cool_hold_temp) <=
                    EcobeeService.MAXIMUM_COOLING_TEMPERATURE):
                raise ValueError('cool_hold_temp must be between {0}F and {1}F'.format(
                    EcobeeService.MINIMUM_COOLING_TEMPERATURE, EcobeeService.MAXIMUM_COOLING_TEMPERATURE))
        if heat_hold_temp is not None:
            if not isinstance(heat_hold_temp, numbers.Real):
                raise TypeError('heat_hold_temp must be an instance of {0}'.format(numbers.Real))
            if not (EcobeeService.MINIMUM_HEATING_TEMPERATURE <= float(heat_hold_temp) <=
                    EcobeeService.MAXIMUM_HEATING_TEMPERATURE):
                raise ValueError('heat_hold_temp must be between {0}F and {1}F'.format(
                    EcobeeService.MINIMUM_HEATING_TEMPERATURE, EcobeeService.MAXIMUM_HEATING_TEMPERATURE))
        if hold_climate_ref is not None and not isinstance(hold_climate_ref, six.string_types):
            raise TypeError('hold_climate_ref must be an instance of {0}'.format(six.string_types))
        if cool_hold_temp is None and heat_hold_temp is None and hold_climate_ref is None:
            raise ValueError('cool_hold_temp, heat_hold_temp, and hold_climate_ref must not all be None. Either '
                             'cool_hold_temp and heat_hold_temp must not be None or hold_climate_ref must not be None')
        if hold_climate_ref is None and (cool_hold_temp is None or heat_hold_temp is None):
            raise ValueError('hold_climate_ref is None. cool_hold_temp and heat_hold_temp must not be None.')
        if start_date_time is not None:
            if not isinstance(start_date_time, datetime):
                raise TypeError('start_date_time must be an instance of {0}'.format(datetime))
            if start_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('start_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if start_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('start_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if end_date_time is not None:
            if not isinstance(end_date_time, datetime):
                raise TypeError('end_date_time must be an instance of {0}'.format(datetime))
            if end_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('end_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if end_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('end_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time is not None and end_date_time is not None and start_date_time >= end_date_time:
            raise ValueError('end_date_time must be later than start_date_time')
        if not isinstance(hold_type, HoldType):
            raise TypeError('hold_type must be an instance of {0}'.format(HoldType))
        if hold_type == HoldType.DATE_TIME and end_date_time is None:
            raise ValueError('hold_type is {0}. end_date_time must not be None'.format(HoldType.DATE_TIME.value))
        if hold_hours is not None and not isinstance(hold_hours, int):
            raise TypeError('hold_hours must be an instance of {0}'.format(int))
        if hold_type == HoldType.HOLD_HOURS and hold_hours is None:
            raise ValueError('hold_type is {0}. hold_hours must not be None'.format(HoldType.HOLD_HOURS.value))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        set_hold_parameters = {'holdType': hold_type.value}
        if cool_hold_temp:
            set_hold_parameters['coolHoldTemp'] = int(cool_hold_temp * 10)
        if heat_hold_temp:
            set_hold_parameters['heatHoldTemp'] = int(heat_hold_temp * 10)
        if hold_climate_ref:
            set_hold_parameters['holdClimateRef'] = hold_climate_ref
        if start_date_time:
            set_hold_parameters['startDate'] = '{0}-{1:02}-{2:02}'.format(start_date_time.year,
                                                                          start_date_time.month, start_date_time.day)
            set_hold_parameters['startTime'] = '{0:02}:{1:02}:{2:02}'.format(start_date_time.hour,
                                                                             start_date_time.minute,
                                                                             start_date_time.second)
        if end_date_time:
            set_hold_parameters['endDate'] = '{0}-{1:02}-{2:02}'.format(end_date_time.year,
                                                                        end_date_time.month, end_date_time.day)
            set_hold_parameters['endTime'] = '{0:02}:{1:02}:{2:02}'.format(end_date_time.hour, end_date_time.minute,
                                                                           end_date_time.second)
        if hold_hours:
            set_hold_parameters['holdHours'] = hold_hours

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='setHold',
                                                           params=set_hold_parameters)],
                                       timeout=timeout)

    def set_occupied(self,
                     occupied,
                     start_date_time=None,
                     end_date_time=None,
                     hold_type=HoldType.INDEFINITE,
                     hold_hours=None,
                     selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                     timeout=5):
        """
        The set_occupied method may only be used by EMS thermostats. The method switches a thermostat from
        occupied mode to unoccupied, or vice versa. If used on a Smart thermostat, the method will throw an error.
        Switch occupancy events are treated as Holds. There may only be one Switch Occupancy at one time, and the new
        event will replace any previous event.

        Note that an occupancy event is created regardless what the program on the thermostat is set to. For example,
        if the program is currently unoccupied and you set occupied=False, an occupancy event will be created using
        the heat/cool settings of the unoccupied program climate. If your intent is to go back to the program
        and remove the occupancy event, use resumeProgram instead.

        :param occupied: The climate to use for the temperature, occupied (True) or unoccupied (False)
        :param start_date_time: The start date and time in thermostat time. Must be a timezone aware datetime
        :param end_date_time: The end date and time in thermostat time. Must be a timezone aware datetime
        :param hold_type: The hold duration type. Valid values: HoldType.DATE_TIME, HoldType.NEXT_TRANSITION,
        HoldType.INDEFINITE, and HoldType.HOLD_HOURS
        :param hold_hours: The number of hours to hold for, used and required if holdType='holdHours'
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If occupied is not a boolean, start_date_time is not a datetime, end_date_time is not a
        datetime, hold_type is not a member of HoldType, hold_hours is not an integer, or selection is not an
        instance of Selection
        :raises ValueError: If start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times
        are later than 2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, end_date_time is None
        while hold_type is HoldType.DATE_TIME, or hold_hours is None while hold_type is HoldType.HOLD_HOURS
        """
        if not isinstance(occupied, bool):
            raise TypeError('occupied must be an instance of {0}'.format(bool))
        if start_date_time is not None:
            if not isinstance(start_date_time, datetime):
                raise TypeError('start_date_time must be an instance of {0}'.format(datetime))
            if start_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('start_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if start_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('start_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if end_date_time is not None:
            if not isinstance(end_date_time, datetime):
                raise TypeError('end_date_time must be an instance of {0}'.format(datetime))
            if end_date_time < EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME:
                raise ValueError('end_date_time must be later than {0}'.format(
                    EcobeeService.BEFORE_TIME_BEGAN_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
            if end_date_time > EcobeeService.END_OF_TIME_DATE_TIME:
                raise ValueError('end_date_time must be earlier than {0}'.format(
                    EcobeeService.END_OF_TIME_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S %Z')))
        if start_date_time is not None and end_date_time is not None and start_date_time >= end_date_time:
            raise ValueError('end_date_time must be later than start_date_time')
        if not isinstance(hold_type, HoldType):
            raise TypeError('hold_type must be an instance of {0}'.format(HoldType))
        if hold_type == HoldType.DATE_TIME and end_date_time is None:
            raise ValueError('hold_type is {0}. end_date_time must not be None'.format(HoldType.DATE_TIME.value))
        if hold_hours is not None and not isinstance(hold_hours, int):
            raise TypeError('hold_hours must be an instance of {0}'.format(int))
        if hold_type == HoldType.HOLD_HOURS and hold_hours is None:
            raise ValueError('hold_type is {0}. hold_hours must not be None'.format(HoldType.HOLD_HOURS.value))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        set_occupied_parameters = {'occupied': occupied, 'holdType': hold_type.value}
        if start_date_time:
            set_occupied_parameters['startDate'] = '{0}-{1:02}-{2:02}'.format(start_date_time.year,
                                                                              start_date_time.month,
                                                                              start_date_time.day)
            set_occupied_parameters['startTime'] = '{0:02}:{1:02}:{2:02}'.format(start_date_time.hour,
                                                                                 start_date_time.minute,
                                                                                 start_date_time.second)
        if end_date_time:
            set_occupied_parameters['endDate'] = '{0}-{1:02}-{2:02}'.format(end_date_time.year, end_date_time.month,
                                                                            end_date_time.day)
            set_occupied_parameters['endTime'] = '{0:02}:{1:02}:{2:02}'.format(end_date_time.hour,
                                                                               end_date_time.minute,
                                                                               end_date_time.second)
        if hold_hours:
            set_occupied_parameters['holdHours'] = hold_hours

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='setOccupied',
                                                           params=set_occupied_parameters)],
                                       timeout=timeout)

    def unlink_voice_engine(self,
                            engine_name,
                            selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                            timeout=5):
        """
        The unlink voice engine function allows you to disable voice assistant for the selected thermostat.

        :param engine_name: The name of the engine to unlink
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If engine_name is not a string or selection is not an instance of Selection
        """
        if not isinstance(engine_name, six.string_types):
            raise TypeError('engine_name must be an instance of {0}'.format(six.string_types))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='unlinkVoiceEngine',
                                                           params={'engineName': engine_name})],
                                       timeout=timeout)

    def update_sensor(self,
                      name,
                      device_id,
                      sensor_id,
                      selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match=''),
                      timeout=5):
        """
        The update_sensor method allows the caller to update the name of an ecobee3 remote sensor. Each ecobee3
        remote sensor "enclosure" contains two distinct sensors types temperature and occupancy. Only one of the
        sensors is required in the request. Both of the sensors' names will be updated to ensure consistency as they
        are part of the same remote sensor enclosure. This also reflects accurately what happens on the
        Thermostat itself.

        :param name: The updated name to give the sensor
        :param device_id: The device_id for the sensor, typically this indicates the enclosure and corresponds to the
        ThermostatRemoteSensor.id attribute
        :param sensor_id: The identifier for the sensor within the enclosure. Corresponds to the
        RemoteSensorCapability.id attribute
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If name is not a string, device_id is not a string, sensor_id is not a string,
        or selection is not an instance of Selection
        :raises ValueError: If name has a length greater than 32
        """
        if not isinstance(name, six.string_types):
            raise TypeError('name must be an instance of {0}'.format(six.string_types))
        if len(name) > 32:
            raise ValueError('name maximum length must not be greater than 32')
        if not isinstance(device_id, six.string_types):
            raise TypeError('device_id must be an instance of {0}'.format(six.string_types))
        if not isinstance(sensor_id, six.string_types):
            raise TypeError('sensor_id must be an instance of {0}'.format(six.string_types))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='updateSensor',
                                                           params={'name': name,
                                                                   'deviceId': device_id,
                                                                   'sensorId': sensor_id})],
                                       timeout=timeout)

    @property
    def thermostat_name(self):
        return self._thermostat_name

    @property
    def application_key(self):
        return self._application_key

    @application_key.setter
    def application_key(self, application_key):
        self._application_key = application_key

    @property
    def authorization_token(self):
        return self._authorization_token

    @authorization_token.setter
    def authorization_token(self, authorization_token):
        self._authorization_token = authorization_token

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        self._refresh_token = refresh_token

    @property
    def access_token_expires_on(self):
        return self._access_token_expires_on

    @access_token_expires_on.setter
    def access_token_expires_on(self, access_token_expires_on):
        self._access_token_expires_on = access_token_expires_on

    @property
    def refresh_token_expires_on(self):
        return self._refresh_token_expires_on

    @refresh_token_expires_on.setter
    def refresh_token_expires_on(self, refresh_token_expires_on):
        self._refresh_token_expires_on = refresh_token_expires_on

    @property
    def scope(self):
        return self._scope
