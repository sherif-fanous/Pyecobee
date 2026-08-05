import json
import logging
from typing import Any

from pyecobee.objects.hierarchy_privilege import HierarchyPrivilege
from pyecobee.objects.hierarchy_user import HierarchyUser
from pyecobee.responses import (
    EcobeeListHierarchySetsResponse,
    EcobeeListHierarchyUsersResponse,
    EcobeeStatusResponse,
)
from pyecobee.services.context import ClientContext
from pyecobee.utilities import Utilities

logger = logging.getLogger(__name__)


class DomainComponent:
    """Base interface for an Ecobee API domain."""

    __slots__ = ("_context",)

    def __init__(self, context: ClientContext):
        self._context = context


class HierarchyService(DomainComponent):
    def list_hierarchy_sets(
        self,
        set_path,
        recursive=False,
        include_privileges=False,
        include_thermostats=False,
        timeout=5,
    ):
        """
        The list_hierarchy_sets method returns the management set
        hierarchy either at a single node depth and its children or
        recursively starting from the node path specified.

        :param set_path: The management set path
        :param recursive: Whether to also return the children of the
        children, recursively. Default: False
        :param include_privileges: Whether to include the privileges
        with each set. Default: False
        :param include_thermostats: Whether to include a list of all
        thermostat identifiers assigned to each set. Default: False
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A ListHierarchySetsResponse object
        :rtype: EcobeeListHierarchySetsResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, recursive is not
        a boolean, include_privileges is not a boolean, or
        include_thermostats is not a boolean
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(recursive, bool):
            raise TypeError(f"recursive must be an instance of {bool}")
        if not isinstance(include_privileges, bool):
            raise TypeError(f"include_privileges must be an instance of {bool}")
        if not isinstance(include_thermostats, bool):
            raise TypeError(f"include_thermostats must be an instance of {bool}")

        dictionary = {
            "operation": "list",
            "setPath": set_path,
            "recursive": recursive,
            "includePrivileges": include_privileges,
            "includeThermostats": include_thermostats,
        }

        response = self._context._transport.request(
            "get",
            ClientContext.HIERARCHY_SET_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return Utilities.process_http_response(
            response, EcobeeListHierarchySetsResponse
        )

    def list_hierarchy_users(
        self, set_path, recursive=False, include_privileges=False, timeout=5
    ):
        """
        The list_hierarchy_users method returns a list hierarchy users
        and privileges.

        :param set_path: The management set path
        :param recursive: Whether to also return the children of the
        children, recursively. Default: False
        :param include_privileges: Whether to include the privileges
        with each set. Default: False
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A ListHierarchyUsersResponse object
        :rtype: EcobeeListHierarchyUsersResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, recursive is not
        a boolean, of include_privileges is not a boolean
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(recursive, bool):
            raise TypeError(f"recursive must be an instance of {bool}")
        if not isinstance(include_privileges, bool):
            raise TypeError(f"include_privileges must be an instance of {bool}")

        dictionary = {
            "operation": "list",
            "setPath": set_path,
            "recursive": recursive,
            "includePrivileges": include_privileges,
        }

        response = self._context._transport.request(
            "get",
            ClientContext.HIERARCHY_USER_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={
                "format": "json",
                "body": json.dumps(dictionary, sort_keys=True, indent=2),
            },
            timeout=timeout,
        )

        return Utilities.process_http_response(
            response, EcobeeListHierarchyUsersResponse
        )

    def add_hierarchy_set(self, set_name, parent_path, timeout=5):
        """
        The add_hierarchy_set adds a new set to the hierarchy.

        :param set_name: The name of the new set
        :param parent_path: The path to the parent for the new set
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, or parent_path
        is not a string
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be an instance of {str}")
        if not isinstance(parent_path, str):
            raise TypeError(f"parent_path must be an instance of {str}")

        dictionary = {
            "operation": "add",
            "setName": set_name,
            "parentPath": parent_path,
        }

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_SET_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def remove_hierarchy_set(self, set_path, timeout=5):
        """
        The remove_hierarchy_set method removes a set from the
        hierarchy.

        :param set_path: The path of the set to delete
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")

        dictionary = {"operation": "remove", "setPath": set_path}

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_SET_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def rename_hierarchy_set(self, set_path, new_name, timeout=5):
        """
        The rename_hierarchy_set method renames a set in the hierarchy.

        :param set_path: The path of the set to rename
        :param new_name: The new name to assign. Must be unique to that
        parent
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, or new_name is
        not a string
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(new_name, str):
            raise TypeError(f"new_name must be an instance of {str}")

        dictionary = {"operation": "rename", "setPath": set_path, "newName": new_name}

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_SET_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def move_hierarchy_set(self, set_path, to_path, timeout=5):
        """
        The move_hierarchy_set method moves a set to a new parent in the
        hierarchy. A parent may not be moved into its own child, nor can
        a set be moved into itself.

        :param set_path: The path of the set to move
        :param to_path: The path of the new parent to move to
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, or to_path is
        not a string
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(to_path, str):
            raise TypeError(f"to_path must be an instance of {str}")

        dictionary = {"operation": "move", "setPath": set_path, "toPath": to_path}

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_SET_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def add_hierarchy_users(self, users, privileges=None, timeout=5):
        """
        The add_hierarchy_users method adds one or more new users to the
        hierarchy and optionally assigns privileges to the new users.
        The privileges being added must be only for the new users being
        added. If no privileges are provided, the user will be a member
        of the hierarchy but will not have access to any sets.

        When a new user is added, an invitation email is sent to the
        email provided as the userName property, which must be a valid
        email address. The user must then click on the invitation link
        to complete their registration.

        :param users: The list of users to add
        :param privileges: The privileges to assign to the new users
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If users is not a list, any member of users
        is not an instance of HierarchyUser, privileges is not a list,
        or any member of privileges is not an instance of
        HierarchyPrivilege
        """
        if not isinstance(users, list):
            raise TypeError(f"users must be an instance of {list}")
        for user in users:
            if not isinstance(user, HierarchyUser):
                raise TypeError(
                    f"All members of users must be a an instance of {HierarchyUser}"
                )
        if privileges is not None:
            if not isinstance(privileges, list):
                raise TypeError(f"privileges must be an instance of {list}")
            for privilege in privileges:
                if not isinstance(privilege, HierarchyPrivilege):
                    raise TypeError(
                        "All members of privileges must be a an instance of "
                        f"{HierarchyPrivilege}"
                    )

        dictionary = {
            "operation": "add",
            "users": [Utilities.object_to_dictionary(user) for user in users],
        }

        if privileges is not None:
            dictionary["privileges"] = [
                Utilities.object_to_dictionary(privilege) for privilege in privileges
            ]

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_USER_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def remove_hierarchy_users(self, set_path, users, timeout=5):
        """
        The remove_hierarchy_users method removes one or more user
        privileges from a set. Only the privileges are removed from the
        specified set, the user remains in the hierarchy.

        :param set_path: The path to the set to remove user privileges
        from
        :param users: The users whose privileges to remove from the set
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, users is not a
        list, or any member of users is not an instance of HierarchyUser
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(users, list):
            raise TypeError(f"users must be an instance of {list}")
        for user in users:
            if not isinstance(user, HierarchyUser):
                raise TypeError(
                    f"All members of users must be a an instance of {HierarchyUser}"
                )

        dictionary = {
            "operation": "remove",
            "setPath": set_path,
            "users": [Utilities.object_to_dictionary(user) for user in users],
        }

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_USER_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def unregister_hierarchy_users(self, users, timeout=5):
        """
        The unregister_hierarchy_users method unregisters the user
        completely from the hierarchy and deletes the account. All set
        privileges are revoked.

        :param users: The users whose privileges to unregister
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If users is not a list, or any member of
        users is not an instance of HierarchyUser
        """
        if not isinstance(users, list):
            raise TypeError(f"users must be an instance of {list}")
        for user in users:
            if not isinstance(user, HierarchyUser):
                raise TypeError(
                    f"All members of users must be a an instance of {HierarchyUser}"
                )

        dictionary = {
            "operation": "unregister",
            "users": [Utilities.object_to_dictionary(user) for user in users],
        }

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_USER_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def update_hierarchy_users(self, users=None, privileges=None, timeout=5):
        """
        The update_hierarchy_users method updates hierarchy user
        information and may update or add privileges to existing
        hierarchy users.

        :param users: The list of users to update
        :param privileges: The privileges to update or add
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If users is not a list, any member of users
        is not an instance of HierarchyUser, privileges is not a list,
        or any member of privileges is not an instance of
        HierarchyPrivilege
        :raises ValueError: If users is None and privileges is None
        """
        if users is not None:
            if not isinstance(users, list):
                raise TypeError(f"users must be an instance of {list}")
            for user in users:
                if not isinstance(user, HierarchyUser):
                    raise TypeError(
                        f"All members of users must be a an instance of {HierarchyUser}"
                    )
        if privileges is not None:
            if not isinstance(privileges, list):
                raise TypeError(f"privileges must be an instance of {list}")
            for privilege in privileges:
                if not isinstance(privilege, HierarchyPrivilege):
                    raise TypeError(
                        "All members of privileges must be a an instance of "
                        f"{HierarchyPrivilege}"
                    )
        if users is None and privileges is None:
            raise ValueError(
                "Either users must not be None or privileges must not be None"
            )

        dictionary: dict[str, Any] = {"operation": "update"}

        if users is not None:
            dictionary["users"] = [
                Utilities.object_to_dictionary(user) for user in users
            ]
        if privileges is not None:
            dictionary["privileges"] = [
                Utilities.object_to_dictionary(privilege) for privilege in privileges
            ]
        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_USER_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def register_hierarchy_thermostats(self, thermostats, set_path=None, timeout=5):
        """
        The register_hierarchy_thermostats method registers one or more
        thermostats with the hierarchy and optionally assigns them to a
        hierarchy set.

        :param set_path: The set path to assign thermostat to
        :param thermostats: Comma separated list of thermostat
        identifiers to register
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If thermostats is not a string, or set_path
        is not a string
        """
        if not isinstance(thermostats, str):
            raise TypeError(f"thermostats must be an instance of {str}")
        if set_path is not None:
            if not isinstance(set_path, str):
                raise TypeError(f"set_path must be an instance of {str}")

        dictionary = {"operation": "register", "thermostats": thermostats}

        if set_path is not None:
            dictionary["setPath"] = set_path

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_THERMOSTAT_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def unregister_hierarchy_thermostats(self, thermostats, timeout=5):
        """
        The unregister_hierarchy_thermostats method unregisters one or
        more thermostat from the hierarchy. The thermostat is completely
        disassociated from the hierarchy.

        :param thermostats: Comma separated list of thermostat
        identifiers to unregister
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If thermostats is not a string
        """
        if not isinstance(thermostats, str):
            raise TypeError(f"thermostats must be an instance of {str}")

        dictionary = {"operation": "unregister", "thermostats": thermostats}

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_THERMOSTAT_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def move_hierarchy_thermostats(
        self, set_path, to_path, thermostats=None, timeout=5
    ):
        """
        The move_hierarchy_thermostats method moves thermostats between
        hierarchy sets. A thermostat may only reside inside a single
        set. Users may be moved in and out of the Unassigned set.
        :param set_path: The set path the thermostats are being moved
        from
        :param to_path: The set path the thermostats are being moved to
        :param thermostats: Comma separated list of thermostat
        identifiers to move. If this argument is None, all thermostats
        which reside in the set_path will be moved
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, to_path is not a
        string, or thermostats is not a string
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(to_path, str):
            raise TypeError(f"to_path must be an instance of {str}")
        if thermostats is not None:
            if not isinstance(thermostats, str):
                raise TypeError(f"thermostats must be an instance of {str}")

        dictionary = {"operation": "move", "setPath": set_path, "toPath": to_path}

        if thermostats is not None:
            dictionary["thermostats"] = thermostats

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_THERMOSTAT_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)

    def assign_hierarchy_thermostats(self, set_path, thermostats, timeout=5):
        """
        The assign_hierarchy_thermostats method forcefully moves one or
        more thermostats from their current set to the specified set. At
        the end of the successful operation the thermostat(s) will be in
        the specified set.

        :param set_path: The set path the thermostats are being moved to
        :param thermostats: Comma separated list of thermostat
        identifiers to assign
        :param timeout: Number of seconds requests will wait to
        establish a connection and to receive a response
        :return: A HierarchyResponse object
        :rtype: EcobeeStatusResponse
        :raises EcobeeApiException: If the request results in an ecobee
        API error response
        :raises EcobeeRequestsException: If an exception is raised by
        the underlying requests module
        :raises TypeError: If set_path is not a string, or thermostats
        is not a string
        """
        if not isinstance(set_path, str):
            raise TypeError(f"set_path must be an instance of {str}")
        if not isinstance(thermostats, str):
            raise TypeError(f"thermostats must be an instance of {str}")

        dictionary = {
            "operation": "assign",
            "setPath": set_path,
            "thermostats": thermostats,
        }

        response = self._context._transport.request(
            "post",
            ClientContext.HIERARCHY_THERMOSTAT_URL,
            headers={
                "Authorization": f"Bearer {self._context._access_token}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            params={"format": "json"},
            json_=dictionary,
            timeout=timeout,
        )

        return Utilities.process_http_response(response, EcobeeStatusResponse)
