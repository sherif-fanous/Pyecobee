import json
import logging
import numbers
import sys
from datetime import datetime
from datetime import timedelta

import pytz
import requests
from six import reraise as raise_

from . import utilities
from .enumerations import AckType
from .enumerations import FanMode
from .enumerations import HoldType
from .enumerations import PlugState
from .enumerations import Scope
from .enumerations import SelectionType
from .exceptions import EcobeeApiException
from .exceptions import EcobeeAuthorizationException
from .exceptions import EcobeeHttpException
from .exceptions import EcobeeRequestsException
from .objects.function import Function
from .objects.selection import Selection
from .objects.status import Status
from .objects.thermostat import Thermostat
from .response import AuthorizeResponse
from .response import ErrorResponse
from .response import MeterReportResponse
from .response import RuntimeReportResponse
from .response import ThermostatResponse
from .response import ThermostatSummaryResponse
from .response import TokensResponse
from .response import UpdateThermostatResponse

logger = logging.getLogger(__name__)


class EcobeeService(object):
    __slots__ = ['_thermostat_name', '_application_key', '_authorization_token', '_access_token', '_refresh_token',
                 '_access_token_expires_on', '_refresh_token_expires_on', '_scope']

    AUTHORIZE_URL = 'https://api.ecobee.com/authorize'
    TOKENS_URL = 'https://api.ecobee.com/token'
    THERMOSTAT_SUMMARY_URL = 'https://api.ecobee.com/1/thermostatSummary'
    THERMOSTAT_URL = 'https://api.ecobee.com/1/thermostat'
    METER_REPORT_URL = 'https://api.ecobee.com/1/meterReport'
    RUNTIME_REPORT_URL = 'https://api.ecobee.com/1/runtimeReport'

    BEFORE_TIME_BEGAN_DATE_TIME = datetime.strptime('2008-01-02 00:00:00 +0000', '%Y-%m-%d %H:%M:%S %z')
    END_OF_TIME_DATE_TIME = datetime.strptime('2035-01-01 00:00:00 +0000', '%Y-%m-%d %H:%M:%S %z')

    MINIMUM_COOLING_TEMPERATURE = -10
    MAXIMUM_COOLING_TEMPERATURE = 120
    MINIMUM_HEATING_TEMPERATURE = 45
    MAXIMUM_HEATING_TEMPERATURE = 120

    def __init__(self, thermostat_name, application_key, authorization_token=None,
                 access_token=None, refresh_token=None, access_token_expires_on=None,
                 refresh_token_expires_on=None, scope=Scope.SMART_WRITE):
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
        if not isinstance(application_key, str):
            raise TypeError('application_key must be an instance of {0}'.format(str))
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

    def __repr__(self):
        return '{0}('.format(self.__class__.__name__) + ', '.join(
            ['{0}={1!r}'.format(attribute_name[1:], getattr(self, attribute_name)) for attribute_name in
             self.__slots__]) + ')'

    def __str__(self):
        return '{0}('.format(self.__class__.__name__) + ', '.join(
            ['_{0}={1!s}'.format(attribute_name[1:], getattr(self, attribute_name)) for attribute_name in
             self.__slots__]) + ')'

    @staticmethod
    def __process_http_response(response, response_class):
        if response.status_code == requests.codes.ok:
            return utilities.dictionary_to_object({response_class.__name__: response.json()},
                                                  {response_class.__name__: response_class},
                                                  {response_class.__name__: None},
                                                  is_top_level=True)
        else:
            if 'error' in response.json():
                error_response = utilities.dictionary_to_object({'ErrorResponse': response.json()},
                                                                {'ErrorResponse': ErrorResponse},
                                                                {'ErrorResponse': None},
                                                                is_top_level=True)
                raise EcobeeAuthorizationException(
                    'ecobee authorization error encountered for URL => {0}\nHTTP error code => {1}\nError type => {'
                    '2}\nError description => {3}\nError URI => {4}'.format(response.request.url,
                                                                            response.status_code,
                                                                            error_response.error,
                                                                            error_response.error_description,
                                                                            error_response.error_uri))
            elif 'status' in response.json():
                status = utilities.dictionary_to_object({'Status': response.json()['status']},
                                                        {'Status': Status},
                                                        {'Status': None},
                                                        is_top_level=True)
                raise EcobeeApiException(
                    'ecobee API error encountered for URL => {0}\nHTTP error code => {1}\nStatus code => {'
                    '2}\nStatus message => {3}'.format(response.request.url,
                                                       response.status_code,
                                                       status.code,
                                                       status.message))
            else:
                raise EcobeeHttpException(
                    'HTTP error encountered for URL => {0}\nHTTP error code => {1}'.format(response.request.url,
                                                                                           response.status_code))

    @staticmethod
    def __make_http_request(requests_http_method, url, headers=None, params=None, json=None, timeout=5):
        try:
            return requests_http_method(url,
                                        headers=headers,
                                        params=params,
                                        json=json,
                                        timeout=timeout)
        except requests.exceptions.RequestException as re:
            traceback = sys.exc_info()[2]
            raise_(EcobeeRequestsException, re.message, traceback)

    def authorize(self, response_type='ecobeePin', timeout=5):
        """
        The authorize method allows a 3rd party application to obtain an authorization code and a 4 byte alphabetic 
        string which can be displayed to the user. The user then logs into the ecobee Portal and registers the 
        application using the PIN provided. Once this step is completed, the 3rd party application is able to 
        request the access and refresh tokens using the request_tokens method.
        
        :param response_type: This is always "ecobeePin"
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An AuthorizeResponse object
        :rtype: AuthorizeResponse
        :raises EcobeeAuthorizationException: If the request results in a standard or extended OAuth error 
        response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module 
        :raises TypeError: If response_type is not a string
        :raises ValueError: If response_type is not set to "ecobeePin"
        """
        if not isinstance(response_type, str):
            raise TypeError('response_type must be an instance of {0}'.format(str))
        if response_type != 'ecobeePin':
            raise ValueError('response_type must be "ecobeePin"')

        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.AUTHORIZE_URL,
                                                     params={'client_id': self._application_key,
                                                             'response_type': response_type,
                                                             'scope': self._scope.value},
                                                     timeout=timeout)
        authorize_response = EcobeeService.__process_http_response(response, AuthorizeResponse)
        self._authorization_token = authorize_response.code
        return authorize_response

    def request_tokens(self, grant_type='ecobeePin', timeout=5):
        """
        The request_tokens method is used to request the access and refresh tokens once the user has authorized the 
        application within the ecobee Web Portal.
        
        :param grant_type: This is always "ecobeePin"
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: A TokensResponse object
        :rtype: TokensResponse
        :raises EcobeeAuthorizationException: If the request results in a standard or extended OAuth error 
        response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If grant_type is not a string
        :raises ValueError: If grant_type is not set to "ecobeePin"
        """
        if not isinstance(grant_type, str):
            raise TypeError('grant_type must be an instance of {0}'.format(str))
        if grant_type != 'ecobeePin':
            raise ValueError('grant_type must be "ecobeePin"')

        now_utc = datetime.now(pytz.utc)
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.TOKENS_URL,
                                                     params={'client_id': self._application_key,
                                                             'code': self._authorization_token,
                                                             'grant_type': grant_type},
                                                     timeout=timeout)
        tokens_response = EcobeeService.__process_http_response(response, TokensResponse)
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
        :rtype: TokensResponse
        :raises EcobeeAuthorizationException: If the request results in a standard or extended OAuth error 
        response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If grant_type is not a string
        :raises ValueError: If grant_type is not set to "refresh_token"
        """
        if not isinstance(grant_type, str):
            raise TypeError('grant_type must be an instance of {0}'.format(str))
        if grant_type != 'refresh_token':
            raise ValueError('grant_type must be "refresh_token"')

        now_utc = datetime.now(pytz.utc)
        response = EcobeeService.__make_http_request(requests.post,
                                                     EcobeeService.TOKENS_URL,
                                                     params={'client_id': self._application_key,
                                                             'code': self._refresh_token,
                                                             'grant_type': grant_type},
                                                     timeout=timeout)
        tokens_response = EcobeeService.__process_http_response(response, TokensResponse)
        self._access_token = tokens_response.access_token
        self._access_token_expires_on = now_utc + timedelta(seconds=tokens_response.expires_in)
        self._refresh_token = tokens_response.refresh_token
        self._refresh_token_expires_on = now_utc + timedelta(days=365)
        return tokens_response

    def request_thermostat_summary(self, selection, timeout=5):
        """
        The request_thermostat_summary method retrieves a list of thermostat configuration and state 
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
        :rtype: ThermostatSummaryResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection))}
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.THERMOSTAT_SUMMARY_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(self._access_token),
                                                              'Content-Type': 'text/json'},
                                                     params={'json': json.dumps(dictionary)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, ThermostatSummaryResponse)

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
        :rtype: ThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If selection is not an instance of Selection
        """
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection))}
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.THERMOSTAT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(self._access_token),
                                                              'Content-Type': 'text/json'},
                                                     params={'json': json.dumps(dictionary)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, ThermostatResponse)

    def update_thermostats(self, selection, thermostat=None, functions=[], timeout=5):
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
        :rtype: UpdateThermostatResponse
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
        if not isinstance(functions, list):
            raise TypeError('functions must be an instance of {0}'.format(list))
        if functions:
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
                                                     headers={'Authorization': 'Bearer {0}'.format(self._access_token),
                                                              'Content-Type': 'text/json'},
                                                     json=dictionary,
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, UpdateThermostatResponse)

    def request_meter_report(self, selection, start_date_time, end_date_time, meters='energy', timeout=5):
        """
        The request_meter_report method retrieves the historical meter reading information for a selection of 
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
        :rtype: MeterReportResponse
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
        if not isinstance(meters, str):
            raise TypeError('meters must be an instance of {0}'.format(str))
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
                      'endInterval': (end_date_time.hour) * 12 + (end_date_time.minute // 5),
                      'meters': meters
                      }
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.METER_REPORT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(self._access_token),
                                                              'Content-Type': 'text/json'},
                                                     params={'json': json.dumps(dictionary)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, MeterReportResponse)

    def request_runtime_report(self, selection, start_date_time, end_date_time, columns, include_sensors=False,
                               timeout=5):
        """
        The request_runtime_report request is limited to retrieving information for up to 25 thermostats with a 
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
        :rtype: RuntimeReportResponse
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
        if not isinstance(columns, str):
            raise TypeError('columns must be an instance of {0}'.format(str))
        if not isinstance(include_sensors, bool):
            raise TypeError('include_sensors must be an instance of {0}'.format(bool))

        utc = pytz.utc
        start_date_time = start_date_time.astimezone(utc)
        end_date_time = end_date_time.astimezone(utc)

        dictionary = {'selection': utilities.object_to_dictionary(selection, type(selection)),
                      'startDate': '{0}-{1:02}-{2:02}'.format(start_date_time.year, start_date_time.month,
                                                              start_date_time.day),
                      'startInterval': (start_date_time.hour * 12) + (start_date_time.minute // 5),
                      'endDate': '{0}-{1:02}-{2:02}'.format(end_date_time.year, end_date_time.month, end_date_time.day),
                      'endInterval': (end_date_time.hour) * 12 + (end_date_time.minute // 5),
                      'columns': columns,
                      'includeSensors': include_sensors
                      }
        response = EcobeeService.__make_http_request(requests.get,
                                                     EcobeeService.RUNTIME_REPORT_URL,
                                                     headers={'Authorization': 'Bearer {0}'.format(self._access_token),
                                                              'Content-Type': 'text/json'},
                                                     params={'json': json.dumps(dictionary)},
                                                     timeout=timeout)
        return EcobeeService.__process_http_response(response, RuntimeReportResponse)

    def acknowledge(self, thermostat_identifier, ack_ref, ack_type, remind_me_later=False, selection=Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match=''), timeout=5):
        """
        The acknowledge method allows an alert to be acknowledged.
        
        :param thermostat_identifier: The thermostat identifier to acknowledge the alert for
        :param ack_ref: The acknowledge ref of alert
        :param ack_type: The type of acknowledgement. Valid values: accept, decline, defer, unacknowledged
        :param remind_me_later: Whether to remind at a later date, if this is a defer acknowledgement
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If thermostat_identifier is not a string, ack_ref is not a string, ack_type is not a 
        member of AckType, remind_me_later is not a boolean, or selection is not an instance of Selection
        """
        if not isinstance(thermostat_identifier, str):
            raise TypeError('thermostat_identifier must be an instance of {0}'.format(str))
        if not isinstance(ack_ref, str):
            raise TypeError('ack_ref must be an instance of {0}'.format(str))
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

    def control_plug(self, plug_name, plug_state, start_date_time=None, end_date_time=None,
                     hold_type=HoldType.INDEFINITE, hold_hours=None, selection=Selection(
                selection_type=SelectionType.REGISTERED.value, selection_match=''), timeout=5):
        """
        The control_plug method controls the on/off state of a plug by setting a hold on the plug, createing a hold for 
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
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If plug_name is not a string, plug_state is not a member of PlugState, start_date_time is 
        not a datetime, end_date_time is not a datetime, hold_type is not a member of HoldType, hold_hours is not an 
        integer, or selection is not an instance of Selection
        :raises ValueError: If start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times 
        are later than 2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, end_date_time is None 
        while hold_type is HoldType.DATE_TIME, or hold_hours is None while hold_type is HoldType.HOLD_HOURS
        """
        if not isinstance(plug_name, str):
            raise TypeError('plug_name must be an instance of {0}'.format(str))
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

    def create_vacation(self, name, cool_hold_temp, heat_hold_temp, start_date_time=None, end_date_time=None,
                        fan_mode=FanMode.AUTO, fan_min_on_time=0, selection=Selection(
                selection_type=SelectionType.REGISTERED.value, selection_match=''), timeout=5):
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
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If name is not a string, cool_hold_temp is not a real number, heat_hold_temp is not a real
        number, start_date_time is not a datetime, end_date_time is not a datetime, fan_mode is not a member of FanMode,
        fan_min_on_time is not an integer, or selection is not an instance of Selection
        :raises ValueError: If cool_hold_temp is lower than -10°F, cool_hold_temp is higher than 120°F, 
        heat_hold_temp is lower than 45°F, heat_hold_temp is higher than 120°F, start/end date_times are earlier than 
        2008-01-02 00:00:00 +0000, start/end date_times are later than 2035-01-01 00:00:00 +0000, start_date_time is 
        later than end_date_time, or fan_min_on_time is less than 0 or greater than 60
        """
        if not isinstance(name, str):
            raise TypeError('name must be an instance of {0}'.format(str))
        if not isinstance(cool_hold_temp, numbers.Real):
            raise TypeError('cool_hold_temp must be an instance of {0}'.format(numbers.Real))
        if not (EcobeeService.MINIMUM_COOLING_TEMPERATURE <= cool_hold_temp <=
                    EcobeeService.MAXIMUM_COOLING_TEMPERATURE):
            raise ValueError('cool_hold_temp must be between {0}F and {1}F'.format(
                EcobeeService.MINIMUM_COOLING_TEMPERATURE, EcobeeService.MAXIMUM_COOLING_TEMPERATURE))
        if not isinstance(heat_hold_temp, numbers.Real):
            raise TypeError('heat_hold_temp must be an instance of {0}'.format(numbers.Real))
        if not (EcobeeService.MINIMUM_HEATING_TEMPERATURE <= heat_hold_temp <=
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

    def delete_vacation(self, name, selection=Selection(selection_type=SelectionType.REGISTERED.value,
                                                        selection_match=''), timeout=5):
        """
        The delete_vacation method deletes a vacation event from a thermostat. This is the only way to cancel a 
        vacation event. This method is able to remove vacation events not yet started and scheduled in the future.
        
        :param name: The vacation event name to delete
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If name is not a string, or selection is not an instance of Selection
        """
        if not isinstance(name, str):
            raise TypeError('name must be an instance of {0}'.format(str))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='deleteVacation',
                                                           params={'name': name})],
                                       timeout=timeout)

    def reset_preferences(self, selection=Selection(selection_type=SelectionType.REGISTERED.value,
                                                    selection_match=''), timeout=5):
        """
        The reset_preferences method sets all of the user configurable settings back to the factory default values. 
        This method call will not only reset the top level thermostat settings such as hvacMode, lastServiceDate and 
        vent, but also all of the user configurable fields of the Thermostat.Settings and Thermostat.Program objects.
        
        Note that this does not reset all values. For example, the installer settings and wifi details remain untouched.
        
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: UpdateThermostatResponse
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

    def resume_program(self, resume_all=False, selection=Selection(selection_type=SelectionType.REGISTERED.value,
                                                                   selection_match=''), timeout=5):
        """
        The resume_program method removes the currently running event providing the event is not a mandatory demand 
        response event. If the resume_all argument is set to False, the top active event is removed from the stack and 
        the thermostat resumes its program or enters the next event in the stack if one exists. If the resume_all 
        argument is set to True, the method resumes all events and returns the thermostat to its program.
        
        :param resume_all: Should the thermostat be resumed to the next event (False) or to it's program (True)
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: UpdateThermostatResponse
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

    def send_message(self, text, selection=Selection(selection_type=SelectionType.REGISTERED.value,
                                                     selection_match=''), timeout=5):
        """
        The send_message method allows an alert message to be sent to the thermostat. The message properties are 
        same as those of the Alert Object.
        
        :param text: The message text to send. Text will be truncated to 500 characters if longer
        :param selection: The selection criteria for the update
        :param timeout: Number of seconds requests will wait to establish a connection and to receive a response
        :return: An UpdateThermostatResponse object indicating the status of this request
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If text is not a string, or selection is not an instance of Selection
        """
        if not isinstance(text, str):
            raise TypeError('text must be an instance of {0}'.format(str))
        if not isinstance(selection, Selection):
            raise TypeError('selection must be an instance of {0}'.format(Selection))

        return self.update_thermostats(selection,
                                       thermostat=None,
                                       functions=[Function(type='sendMessage',
                                                           params={'text': text})],
                                       timeout=timeout)

    def set_hold(self, cool_hold_temp=None, heat_hold_temp=None, hold_climate_ref=None, start_date_time=None,
                 end_date_time=None, hold_type=HoldType.INDEFINITE, hold_hours=None, selection=Selection(
                selection_type=SelectionType.REGISTERED.value, selection_match=''), timeout=5):
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
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If cool_hold_temp is not a real, heat_hold_temp is not a real, hold_climate_ref is not a 
        string, start_date_time is not a datetime, end_date_time is not a datetime, hold_type is not a member 
        of HoldType, hold_hours is not an integer, or selection is not an instance of Selection
        :raises ValueError: If cool_hold_temp is lower than -10°F, cool_hold_temp is higher than 120°F, 
        heat_hold_temp is lower than 45°F, heat_hold_temp is higher than 120°F, cool_hold_temp, heat_hold_temp, 
        and hold_climate_ref are None, hold_climate_ref is None and either cool_hold_temp or heat_hold_temp are None, 
        start/end date_times are earlier than 2008-01-02 00:00:00 +0000, start/end date_times are later than 
        2035-01-01 00:00:00 +0000, start_date_time is later than end_date_time, end_date_time is None while hold_type 
        is HoldType.DATE_TIME, or hold_hours is None while hold_type is HoldType.HOLD_HOURS
        """
        if cool_hold_temp is not None:
            if not isinstance(cool_hold_temp, numbers.Real):
                raise TypeError('cool_hold_temp must be an instance of {0}'.format(numbers.Real))
            if not (EcobeeService.MINIMUM_COOLING_TEMPERATURE <= cool_hold_temp <=
                        EcobeeService.MAXIMUM_COOLING_TEMPERATURE):
                raise ValueError('cool_hold_temp must be between {0}F and {1}F'.format(
                    EcobeeService.MINIMUM_COOLING_TEMPERATURE, EcobeeService.MAXIMUM_COOLING_TEMPERATURE))
        if heat_hold_temp is not None:
            if not isinstance(heat_hold_temp, numbers.Real):
                raise TypeError('heat_hold_temp must be an instance of {0}'.format(numbers.Real))
            if not (EcobeeService.MINIMUM_HEATING_TEMPERATURE <= heat_hold_temp <=
                        EcobeeService.MAXIMUM_HEATING_TEMPERATURE):
                raise ValueError('heat_hold_temp must be between {0}F and {1}F'.format(
                    EcobeeService.MINIMUM_HEATING_TEMPERATURE, EcobeeService.MAXIMUM_HEATING_TEMPERATURE))
        if hold_climate_ref is not None and not isinstance(hold_climate_ref, str):
            raise TypeError('hold_climate_ref must be an instance of {0}'.format(str))
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

    def set_occupied(self, occupied, start_date_time=None, end_date_time=None, hold_type=HoldType.INDEFINITE,
                     hold_hours=None, selection=Selection(selection_type=SelectionType.REGISTERED.value,
                                                          selection_match=''), timeout=5):
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
        :rtype: UpdateThermostatResponse
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

    def update_sensor(self, name, device_id, sensor_id, selection=Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match=''), timeout=5):
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
        :rtype: UpdateThermostatResponse
        :raises EcobeeApiException: If the request results in an ecobee API error response
        :raises EcobeeRequestsException: If an exception is raised by the underlying requests module
        :raises TypeError: If name is not a string, device_id is not a string, sensor_id is not a string, 
        or selection is not an instance of Selection
        :raises ValueError: If name has a length greater than 32
        """
        if not isinstance(name, str):
            raise TypeError('name must be an instance of {0}'.format(str))
        if len(name) > 32:
            raise ValueError('name maximum length must not be greater than 32')
        if not isinstance(device_id, str):
            raise TypeError('device_id must be an instance of {0}'.format(str))
        if not isinstance(sensor_id, str):
            raise TypeError('sensor_id must be an instance of {0}'.format(str))
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
