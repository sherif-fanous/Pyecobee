from pyecobee.ecobee_object import EcobeeObject


class EcobeeStatusResponse(EcobeeObject):
    __slots__ = ['_status']

    attribute_name_map = {'status': 'status'}

    attribute_type_map = {'status': 'Status'}

    def __init__(self, status):
        """
        Construct a EcobeeStatusResponse instance

        :param status: The api response code
        """
        self._status = status

    @property
    def status(self):
        """
        Gets the status attribute of this EcobeeStatusResponse instance.

        :return: The value of the status attribute of this EcobeeStatusResponse instance.
        :rtype: Status
        """
        return self._status


class EcobeeAuthorizeResponse(EcobeeObject):
    __slots__ = ['_ecobee_pin', '_code', '_scope', '_expires_in', '_interval']

    attribute_name_map = {'ecobee_pin': 'ecobeePin', 'ecobeePin': 'ecobee_pin', 'code': 'code', 'scope': 'scope',
                          'expires_in': 'expires_in', 'interval': 'interval'}

    attribute_type_map = {'ecobee_pin': 'six.text_type', 'code': 'six.text_type', 'scope': 'six.text_type',
                          'expires_in': 'int', 'interval': 'int'}

    def __init__(self, ecobee_pin, code, scope, expires_in, interval):
        """
        Construct an EcobeeAuthorizeResponse instance

        :param ecobee_pin: The PIN a user enters in the web portal
        :param code: The authorization token needed to request the access and refresh tokens
        :param scope: The requested Scope from the original request
        :param expires_in: The number of minutes until the PIN expires
        :param interval: The minimum amount of seconds which must pass between polling attempts for a token
        """
        self._ecobee_pin = ecobee_pin
        self._code = code
        self._scope = scope
        self._expires_in = expires_in
        self._interval = interval

    @property
    def ecobee_pin(self):
        """
        Gets the ecobee_pin attribute of this EcobeeAuthorizeResponse instance.

        :return: The value of the ecobee_pin attribute of this EcobeeAuthorizeResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._ecobee_pin

    @property
    def code(self):
        """
        Gets the code attribute of this EcobeeAuthorizeResponse instance.

        :return: The value of the code attribute of this EcobeeAuthorizeResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._code

    @property
    def scope(self):
        """
        Gets the scope attribute of this EcobeeAuthorizeResponse instance.

        :return: The value of the scope attribute of this EcobeeAuthorizeResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._scope

    @property
    def expires_in(self):
        """
        Gets the expires_in attribute of this EcobeeAuthorizeResponse instance.

        :return: The value of the expires_in attribute of this EcobeeAuthorizeResponse instance.
        :rtype: int
        """
        return self._expires_in

    @property
    def interval(self):
        """
        Gets the interval attribute of this EcobeeAuthorizeResponse instance.

        :return: The value of the interval attribute of this EcobeeAuthorizeResponse instance.
        :rtype: int
        """
        return self._interval


class EcobeeCreateRuntimeReportJobResponse(EcobeeStatusResponse):
    __slots__ = ['_job_id', '_job_status']

    attribute_name_map = {'job_id': 'jobId', 'jobId': 'job_id', 'job_status': 'jobStatus', 'jobStatus': 'job_status',
                          'status': 'status'}

    attribute_type_map = {'job_id': 'six.text_type', 'job_status': 'six.text_type', 'status': 'Status'}

    def __init__(self, job_id, job_status, status):
        """
        Construct a EcobeeCreateRuntimeReportJobResponse instance

        :param job_id: The generated id for the created runtime report job
        :param job_status: The status of the created runtime report job
        :param status: The api response code
        """
        self._job_id = job_id
        self._job_status = job_status
        EcobeeStatusResponse.__init__(self, status)

    @property
    def job_id(self):
        """
        Gets the job_id attribute of this EcobeeCreateRuntimeReportJobResponse instance.

        :return: The value of the job_id attribute of this EcobeeCreateRuntimeReportJobResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._job_id

    @property
    def job_status(self):
        """
        Gets the job_status attribute of this EcobeeCreateRuntimeReportJobResponse instance.

        :return: The value of the job_status attribute of this EcobeeCreateRuntimeReportJobResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._job_status


class EcobeeErrorResponse(EcobeeObject):
    __slots__ = ['_error', '_error_description', '_error_uri']

    attribute_name_map = {'error': 'error', 'error_description': 'error_description', 'error_uri': 'error_uri'}

    attribute_type_map = {'error': 'six.text_type', 'error_description': 'six.text_type', 'error_uri': 'six.text_type'}

    def __init__(self, error, error_description, error_uri):
        """
        Construct an EcobeeErrorResponse instance

        :param error: The error type
        :param error_description: The description of the error
        :param error_uri: The URI of the error
        """
        self._error = error
        self._error_description = error_description
        self._error_uri = error_uri

    @property
    def error(self):
        """
        Gets the error attribute of this EcobeeErrorResponse instance.

        :return: The value of the error attribute of this EcobeeErrorResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._error

    @property
    def error_description(self):
        """
        Gets the error_description attribute of this EcobeeErrorResponse instance.

        :return: The value of the error_description attribute of this EcobeeErrorResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._error_description

    @property
    def error_uri(self):
        """
        Gets the error_uri attribute of this EcobeeErrorResponse instance.

        :return: The value of the error_uri attribute of this EcobeeErrorResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._error_uri


class EcobeeGroupsResponse(EcobeeStatusResponse):
    __slots__ = ['_groups']

    attribute_name_map = {'groups': 'groups', 'status': 'status'}

    attribute_type_map = {'groups': 'List[Group]', 'status': 'Status'}

    def __init__(self, groups, status):
        """
        Construct a EcobeeGroupsResponse instance

        :param groups: The list of Groups returned by the request
        :param status: The api response code
        """
        self._groups = groups
        EcobeeStatusResponse.__init__(self, status)

    @property
    def groups(self):
        """
        Gets the groups attribute of this EcobeeGroupsResponse instance.

        :return: The value of the groups attribute of this EcobeeGroupsResponse instance.
        :rtype: List[Group]
        """
        return self._groups


class EcobeeIssueDemandResponsesResponse(EcobeeStatusResponse):
    __slots__ = ['_demand_response_ref']

    attribute_name_map = {'demand_response_ref': 'demandResponseRef', 'demandResponseRef': 'demand_response_ref',
                          'status': 'status'}

    attribute_type_map = {'demand_response_ref': 'six.text_type', 'status': 'Status'}

    def __init__(self, demand_response_ref, status):
        """
        Construct a EcobeeIssueDemandResponsesResponse instance

        :param demand_response_ref: The unique demand response reference ID
        :param status: The api response code
        """
        self._demand_response_ref = demand_response_ref
        EcobeeStatusResponse.__init__(self, status)

    @property
    def demand_response_ref(self):
        """
        Gets the demand_response_ref attribute of this EcobeeIssueDemandResponsesResponse instance.

        :return: The value of the demand_response_ref attribute of this EcobeeIssueDemandResponsesResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._demand_response_ref


class EcobeeListDemandResponsesResponse(EcobeeStatusResponse):
    __slots__ = ['_demand_response_list']

    attribute_name_map = {'demand_response_list': 'drList', 'drList': 'demand_response_list', 'status': 'status'}

    attribute_type_map = {'demand_response_list': 'List[DemandResponse]', 'status': 'Status'}

    def __init__(self, demand_response_list, status):
        """
        Construct a EcobeeListDemandResponsesResponse instance

        :param demand_response_list: The list of demand responses which have not yet expired
        :param status: The api response code
        """
        self._demand_response_list = demand_response_list
        EcobeeStatusResponse.__init__(self, status)

    @property
    def demand_response_list(self):
        """
        Gets the demand_response_list attribute of this EcobeeListDemandResponsesResponse instance.

        :return: The value of the demand_response_list attribute of this EcobeeListDemandResponsesResponse instance.
        :rtype: List[DemandResponse]
        """
        return self._demand_response_list


class EcobeeListHierarchySetsResponse(EcobeeStatusResponse):
    __slots__ = ['_sets']

    attribute_name_map = {'sets': 'sets', 'status': 'status'}

    attribute_type_map = {'sets': 'List[HierarchySet]', 'status': 'Status'}

    def __init__(self, sets, status):
        """
        Construct a EcobeeListHierarchySetsResponse instance

        :param sets: The list of hierarchy management sets
        :param status: The api response code
        """
        self._sets = sets
        EcobeeStatusResponse.__init__(self, status)

    @property
    def sets(self):
        """
        Gets the sets attribute of this EcobeeListHierarchySetsResponse instance.

        :return: The value of the sets attribute of this EcobeeListHierarchySetsResponse instance.
        :rtype: List[HierarchySet]
        """
        return self._sets


class EcobeeListHierarchyUsersResponse(EcobeeStatusResponse):
    __slots__ = ['_users', '_privileges']

    attribute_name_map = {'users': 'users', 'privileges': 'privileges', 'status': 'status'}

    attribute_type_map = {'users': 'List[HierarchyUser]', 'privileges': 'List[HierarchyPrivilege]',
                          'status': 'Status'}

    def __init__(self, users, status, privileges=None):
        """
        Construct a EcobeeListHierarchyUsersResponse instance

        :param users: The list of users in the company
        :param privileges: List of hierarchy privileges if requested
        :param status: The api response code
        """
        self._users = users
        self._privileges = privileges
        EcobeeStatusResponse.__init__(self, status)

    @property
    def users(self):
        """
        Gets the users attribute of this EcobeeListHierarchyUsersResponse instance.

        :return: The value of the users attribute of this EcobeeListHierarchyUsersResponse instance.
        :rtype: List[HierarchyUser]
        """
        return self._users

    @property
    def privileges(self):
        """
        Gets the privileges attribute of this EcobeeListHierarchyUsersResponse instance.

        :return: The value of the privileges attribute of this EcobeeListHierarchyUsersResponse instance.
        :rtype: List[HierarchyPrivilege]
        """
        return self._privileges


class EcobeeListRuntimeReportJobStatusResponse(EcobeeStatusResponse):
    __slots__ = ['_jobs']

    attribute_name_map = {'jobs': 'jobs', 'status': 'status'}

    attribute_type_map = {'jobs': 'List[ReportJob]', 'status': 'Status'}

    def __init__(self, jobs, status):
        """
        Construct a EcobeeListRuntimeReportJobStatusResponse instance

        :param jobs: The list of report jobs for the corresponding request
        :param status: The api response code
        """
        self._jobs = jobs
        EcobeeStatusResponse.__init__(self, status)

    @property
    def jobs(self):
        """
        Gets the jobs attribute of this EcobeeListRuntimeReportJobStatusResponse instance.

        :return: The value of the jobs attribute of this EcobeeListRuntimeReportJobStatusResponse instance.
        :rtype: List[ReportJob]
        """
        return self._jobs


class EcobeeMeterReportsResponse(EcobeeStatusResponse):
    __slots__ = ['_report_list']

    attribute_name_map = {'report_list': 'reportList', 'reportList': 'report_list', 'status': 'status'}

    attribute_type_map = {'report_list': 'List[MeterReport]', 'status': 'Status'}

    def __init__(self, report_list, status):
        """
        Construct a EcobeeMeterReportsResponse instance

        :param report_list: A list of thermostat meter reports
        :param status: The api response code
        """
        self._report_list = report_list
        EcobeeStatusResponse.__init__(self, status)

    @property
    def report_list(self):
        """
        Gets the report_list attribute of this EcobeeMeterReportsResponse instance.

        :return: The value of the report_list attribute of this EcobeeMeterReportsResponse instance.
        :rtype: List[MeterReport]
        """
        return self._report_list


class EcobeeRuntimeReportsResponse(EcobeeStatusResponse):
    __slots__ = ['_start_date', '_start_interval', '_end_date', '_end_interval', '_columns', '_report_list',
                 '_sensor_list']

    attribute_name_map = {'start_date': 'startDate', 'startDate': 'start_date', 'start_interval': 'startInterval',
                          'startInterval': 'start_interval', 'end_date': 'endDate', 'endDate': 'end_date',
                          'end_interval': 'endInterval', 'endInterval': 'end_interval', 'columns': 'columns',
                          'report_list': 'reportList', 'reportList': 'report_list', 'sensor_list': 'sensorList',
                          'sensorList': 'sensor_list', 'status': 'status'}

    attribute_type_map = {'start_date': 'six.text_type', 'start_interval': 'int', 'end_date': 'six.text_type',
                          'end_interval': 'int', 'columns': 'six.text_type', 'report_list': 'List[RuntimeReport]',
                          'sensor_list': 'List[RuntimeSensorReport]', 'status': 'Status'}

    def __init__(self, start_date, start_interval, end_date, end_interval, columns, report_list, sensor_list, status):
        """
        Construct a EcobeeRuntimeReportsResponse instance

        :param start_date: The report UTC start date
        :param start_interval: The report start interval
        :param end_date: The report UTC end date
        :param end_interval: The report end interval
        :param columns: The CSV list of column names from the request
        :param report_list: A list of runtime reports
        :param sensor_list: A list of runtime sensor reports
        :param status: The api response code
        """
        self._start_date = start_date
        self._start_interval = start_interval
        self._end_date = end_date
        self._end_interval = end_interval
        self._columns = columns
        self._report_list = report_list
        self._sensor_list = sensor_list
        EcobeeStatusResponse.__init__(self, status)

    @property
    def start_date(self):
        """
        Gets the start_date attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the start_date attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._start_date

    @property
    def start_interval(self):
        """
        Gets the start_interval attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the start_interval attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: int
        """
        return self._start_interval

    @property
    def end_date(self):
        """
        Gets the end_date attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the end_date attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._end_date

    @property
    def end_interval(self):
        """
        Gets the end_interval attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the end_interval attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: int
        """
        return self._end_interval

    @property
    def columns(self):
        """
        Gets the columns attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the columns attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._columns

    @property
    def report_list(self):
        """
        Gets the report_list attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the report_list attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: List[RuntimeReport]
        """
        return self._report_list

    @property
    def sensor_list(self):
        """
        Gets the report_list attribute of this EcobeeRuntimeReportsResponse instance.

        :return: The value of the report_list attribute of this EcobeeRuntimeReportsResponse instance.
        :rtype: List[RuntimeSensorReport]
        """
        return self._sensor_list


class EcobeeThermostatResponse(EcobeeStatusResponse):
    __slots__ = ['_page', '_thermostat_list']

    attribute_name_map = {'page': 'page', 'thermostat_list': 'thermostatList', 'thermostatList': 'thermostat_list',
                          'status': 'status'}

    attribute_type_map = {'page': 'Page', 'thermostat_list': 'List[Thermostat]', 'status': 'Status'}

    def __init__(self, page, thermostat_list, status):
        """
        Construct a EcobeeThermostatResponse instance

        :param page: The page information for the response
        :param thermostat_list: The list of thermostats returned by the request
        :param status: The api response code
        """
        self._page = page
        self._thermostat_list = thermostat_list
        EcobeeStatusResponse.__init__(self, status)

    @property
    def page(self):
        """
        Gets the page attribute of this EcobeeThermostatResponse instance.

        :return: The value of the page attribute of this EcobeeThermostatResponse instance.
        :rtype: Page
        """
        return self._page

    @property
    def thermostat_list(self):
        """
        Gets the thermostat_list attribute of this EcobeeThermostatResponse instance.

        :return: The value of the thermostat_list attribute of this EcobeeThermostatResponse instance.
        :rtype: List[Thermostat]
        """
        return self._thermostat_list


class EcobeeThermostatsSummaryResponse(EcobeeStatusResponse):
    __slots__ = ['_revision_list', '_thermostat_count', '_status_list']

    attribute_name_map = {'revision_list': 'revisionList', 'revisionList': 'revision_list',
                          'thermostat_count': 'thermostatCount', 'thermostatCount': 'thermostat_count',
                          'status_list': 'statusList', 'statusList': 'status_list', 'status': 'status'}

    attribute_type_map = {'revision_list': 'List[six.text_type]', 'thermostat_count': 'int',
                          'status_list': 'List[six.text_type]',
                          'status': 'Status'}

    def __init__(self, revision_list, thermostat_count, status_list, status):
        """
        Construct a EcobeeThermostatsSummaryResponse instance

        :param revision_list: The list of CSV revision values
        :param thermostat_count: Number of thermostats listed in the Revision List
        :param status_list: The list of CSV status values
        :param status: The api response code
        """
        self._revision_list = revision_list
        self._thermostat_count = thermostat_count
        self._status_list = status_list
        EcobeeStatusResponse.__init__(self, status)

    @property
    def revision_list(self):
        """
        Gets the revision_list attribute of this EcobeeThermostatsSummaryResponse instance.

        :return: The value of the revision_list attribute of this EcobeeThermostatsSummaryResponse instance.
        :rtype: List[six.text_type] (This is List[unicode()] in Python 2 and List[str] in Python 3)
        """
        return self._revision_list

    @property
    def thermostat_count(self):
        """
        Gets the thermostat_count attribute of this EcobeeThermostatsSummaryResponse instance.

        :return: The value of the thermostat_count attribute of this EcobeeThermostatsSummaryResponse instance.
        :rtype: int
        """
        return self._thermostat_count

    @property
    def status_list(self):
        """
        Gets the status_list attribute of this EcobeeThermostatsSummaryResponse instance.

        :return: The value of the status_list attribute of this EcobeeThermostatsSummaryResponse instance.
        :rtype: List[six.text_type] (This is List[unicode()] in Python 2 and List[str] in Python 3)
        """
        return self._status_list


class EcobeeTokensResponse(EcobeeObject):
    __slots__ = ['_access_token', '_token_type', '_expires_in', '_refresh_token', '_scope']

    attribute_name_map = {'access_token': 'access_token', 'token_type': 'token_type', 'expires_in': 'expires_in',
                          'refresh_token': 'refresh_token', 'scope': 'scope'}

    attribute_type_map = {'access_token': 'six.text_type', 'token_type': 'six.text_type', 'expires_in': 'int',
                          'refresh_token': 'six.text_type', 'scope': 'six.text_type'}

    def __init__(self, access_token, token_type, expires_in, refresh_token, scope):
        """
        Construct a EcobeeTokensResponse instance

        :param access_token: The token to be used to encapsulate the authorization scope and credentials
        :param token_type: Type of token
        :param expires_in: The number of minutes until the PIN expires
        :param refresh_token: The token to be used to refresh an expired access_token
        :param scope: The requested Scope from the original request
        """
        self._access_token = access_token
        self._token_type = token_type
        self._expires_in = expires_in
        self._refresh_token = refresh_token
        self._scope = scope

    @property
    def access_token(self):
        """
        Gets the access_token attribute of this EcobeeTokensResponse instance.

        :return: The value of the access_token attribute of this EcobeeTokensResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._access_token

    @property
    def token_type(self):
        """
        Gets the token_type attribute of this EcobeeTokensResponse instance.

        :return: The value of the token_type attribute of this EcobeeTokensResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._token_type

    @property
    def expires_in(self):
        """
        Gets the expires_in attribute of this EcobeeTokensResponse instance.

        :return: The value of the expires_in attribute of this EcobeeTokensResponse instance.
        :rtype: int
        """
        return self._expires_in

    @property
    def refresh_token(self):
        """
        Gets the refresh_token attribute of this EcobeeTokensResponse instance.

        :return: The value of the refresh_token attribute of this EcobeeTokensResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._refresh_token

    @property
    def scope(self):
        """
        Gets the scope attribute of this EcobeeTokensResponse instance.

        :return: The value of the scope attribute of this EcobeeTokensResponse instance.
        :rtype: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        return self._scope
