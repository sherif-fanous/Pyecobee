class Response(object):
    def pretty_format(self, indent=2, level=0):
        pretty_formatted = ['{0}(\n'.format(self.__class__.__name__)]
        level = level + 1
        for (i, attribute_name) in enumerate(self.__slots__):
            if i:
                pretty_formatted.append(',\n')
            if isinstance(getattr(self, attribute_name), list):
                pretty_formatted.append('{0}{1}=[\n'.format(' ' * (indent * level),
                                                            self.attribute_name_map[attribute_name[1:]]))
                level = level + 1
                for (j, list_entry) in enumerate(getattr(self, attribute_name)):
                    if j:
                        pretty_formatted.append(',\n')
                    if hasattr(list_entry, 'pretty_format'):
                        pretty_formatted.append('{0}{1}'.format(' ' * (indent * level),
                                                                list_entry.pretty_format(indent, level)))
                    else:
                        if isinstance(list_entry, list):
                            pretty_formatted.append('{0}[\n'.format(' ' * (indent * level)))
                            level = level + 1
                            for (k, sub_list_entry) in enumerate(list_entry):
                                if k:
                                    pretty_formatted.append(',\n')
                                pretty_formatted.append('{0}{1}'.format(' ' * (indent * level), sub_list_entry))
                            if list_entry:
                                pretty_formatted.append('\n')
                            level = level - 1
                            pretty_formatted.append('{0}]'.format(' ' * (indent * level)))
                        else:
                            pretty_formatted.append('{0}{1}'.format(' ' * (indent * level), list_entry))
                if getattr(self, attribute_name):
                    pretty_formatted.append('\n')
                level = level - 1
                pretty_formatted.append('{0}]'.format(' ' * (indent * level)))
            else:
                pretty_formatted.append(' ' * (indent * level))
                if hasattr(getattr(self, attribute_name), 'pretty_format'):
                    pretty_formatted.append('{0}={1!s}'.format(self.attribute_name_map[attribute_name[1:]],
                                                               getattr(self, attribute_name).pretty_format(indent,
                                                                                                           level)))
                else:
                    pretty_formatted.append('{0}={1!s}'.format(self.attribute_name_map[attribute_name[1:]],
                                                               getattr(self, attribute_name)))
        level = level - 1
        pretty_formatted.append('\n{0})'.format(' ' * (indent * level)))
        return ''.join(pretty_formatted)

    def __repr__(self):
        return '{0}('.format(self.__class__.__name__) + ', '.join(
            ['{0}={1!r}'.format(attribute_name[1:], getattr(self, attribute_name)) for attribute_name in
             self.__slots__]) + ')'

    def __str__(self):
        return '{0}('.format(self.__class__.__name__) + ', '.join(
            ['{0}={1!s}'.format(type(self).attribute_name_map[attribute_name[1:]], getattr(self, attribute_name)) for
             attribute_name in self.__slots__]) + ')'


class AuthorizeResponse(Response):
    __slots__ = ['_ecobee_pin', '_code', '_scope', '_expires_in', '_interval']

    attribute_name_map = {'ecobee_pin': 'ecobeePin', 'ecobeePin': 'ecobee_pin', 'code': 'code', 'scope': 'scope',
                          'expires_in': 'expires_in', 'interval': 'interval'}

    attribute_type_map = {'ecobee_pin': 'six.text_type', 'code': 'six.text_type', 'scope': 'six.text_type',
                          'expires_in': 'int', 'interval': 'int'}

    def __init__(self, ecobee_pin, code, scope, expires_in, interval):
        self._ecobee_pin = ecobee_pin
        self._code = code
        self._scope = scope
        self._expires_in = expires_in
        self._interval = interval

    @property
    def ecobee_pin(self):
        return self._ecobee_pin

    @property
    def code(self):
        return self._code

    @property
    def scope(self):
        return self._scope

    @property
    def expires_in(self):
        return self._expires_in

    @property
    def interval(self):
        return self._interval


class ErrorResponse(Response):
    __slots__ = ['_error', '_error_description', '_error_uri']

    attribute_name_map = {'error': 'error', 'error_description': 'error_description', 'error_uri': 'error_uri'}

    attribute_type_map = {'error': 'six.text_type', 'error_description': 'six.text_type', 'error_uri': 'six.text_type'}

    def __init__(self, error, error_description, error_uri):
        self._error = error
        self._error_description = error_description
        self._error_uri = error_uri

    @property
    def error(self):
        return self._error

    @property
    def error_description(self):
        return self._error_description

    @property
    def error_uri(self):
        return self._error_uri


class MeterReportResponse(Response):
    __slots__ = ['_report_list', '_status']

    attribute_name_map = {'report_list': 'reportList', 'reportList': 'report_list', 'status': 'status'}

    attribute_type_map = {'report_list': 'List[MeterReport]', 'status': 'Status'}

    def __init__(self, report_list, status):
        self._report_list = report_list
        self._status = status

    @property
    def report_list(self):
        return self._report_list

    @property
    def status(self):
        return self._status


class RuntimeReportResponse(Response):
    __slots__ = ['_start_date', '_start_interval', '_end_date', '_end_interval', '_columns', '_report_list',
                 '_sensor_list', '_status']

    attribute_name_map = {'start_date': 'startDate', 'startDate': 'start_date', 'start_interval': 'startInterval',
                          'startInterval': 'start_interval', 'end_date': 'endDate', 'endDate': 'end_date',
                          'end_interval': 'endInterval', 'endInterval': 'end_interval', 'columns': 'columns',
                          'report_list': 'reportList', 'reportList': 'report_list', 'sensor_list': 'sensorList',
                          'sensorList': 'sensor_list', 'status': 'status'}

    attribute_type_map = {'start_date': 'six.text_type', 'start_interval': 'int', 'end_date': 'six.text_type',
                          'end_interval': 'int', 'columns': 'six.text_type', 'report_list': 'List[RuntimeReport]',
                          'sensor_list': 'List[RuntimeSensorReport]', 'status': 'Status'}

    def __init__(self, start_date, start_interval, end_date, end_interval, columns, report_list, sensor_list, status):
        self._start_date = start_date
        self._start_interval = start_interval
        self._end_date = end_date
        self._end_interval = end_interval
        self._columns = columns
        self._report_list = report_list
        self._sensor_list = sensor_list
        self._status = status

    @property
    def report_list(self):
        return self._report_list

    @property
    def status(self):
        return self._status


class ThermostatResponse(Response):
    __slots__ = ['_page', '_thermostat_list', '_status']

    attribute_name_map = {'page': 'page', 'thermostat_list': 'thermostatList', 'thermostatList': 'thermostat_list',
                          'status': 'status'}

    attribute_type_map = {'page': 'Page', 'thermostat_list': 'List[Thermostat]', 'status': 'Status'}

    def __init__(self, page, thermostat_list, status):
        self._page = page
        self._thermostat_list = thermostat_list
        self._status = status

    @property
    def page(self):
        return self._page

    @property
    def thermostat_list(self):
        return self._thermostat_list

    @property
    def status(self):
        return self._status


class ThermostatSummaryResponse(Response):
    __slots__ = ['_revision_list', '_thermostat_count', '_status_list', '_status']

    attribute_name_map = {'revision_list': 'revisionList', 'revisionList': 'revision_list',
                          'thermostat_count': 'thermostatCount', 'thermostatCount': 'thermostat_count',
                          'status_list': 'statusList', 'statusList': 'status_list', 'status': 'status'}

    attribute_type_map = {'revision_list': 'List[six.text_type]', 'thermostat_count': 'int',
                          'status_list': 'List[six.text_type]',
                          'status': 'Status'}

    def __init__(self, revision_list, thermostat_count, status_list, status):
        self._revision_list = revision_list
        self._thermostat_count = thermostat_count
        self._status_list = status_list
        self._status = status

    @property
    def revision_list(self):
        return self._revision_list

    @property
    def thermostat_count(self):
        return self._thermostat_count

    @property
    def status_list(self):
        return self._status_list

    @property
    def status(self):
        return self._status


class TokensResponse(Response):
    __slots__ = ['_access_token', '_token_type', '_expires_in', '_refresh_token', '_scope']

    attribute_name_map = {'access_token': 'access_token', 'token_type': 'token_type', 'expires_in': 'expires_in',
                          'refresh_token': 'refresh_token', 'scope': 'scope'}

    attribute_type_map = {'access_token': 'six.text_type', 'token_type': 'six.text_type', 'expires_in': 'int',
                          'refresh_token': 'six.text_type',
                          'scope': 'six.text_type'}

    def __init__(self, access_token, token_type, expires_in, refresh_token, scope):
        self._access_token = access_token
        self._token_type = token_type
        self._expires_in = expires_in
        self._refresh_token = refresh_token
        self._scope = scope

    @property
    def access_token(self):
        return self._access_token

    @property
    def token_type(self):
        return self._token_type

    @property
    def expires_in(self):
        return self._expires_in

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def scope(self):
        return self._scope


class UpdateThermostatResponse(Response):
    __slots__ = ['_status']

    attribute_name_map = {'status': 'status'}

    attribute_type_map = {'status': 'Status'}

    def __init__(self, status):
        self._status = status

    @property
    def status(self):
        return self._status
