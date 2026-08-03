import ast
import subprocess
from pathlib import Path

from pyecobee import EcobeeService
from pyecobee.services import (
    AuthorizationService,
    DemandService,
    GroupsService,
    HierarchyService,
    ReportsService,
    ThermostatsService,
)


def test_facade_uses_a_component_for_each_api_domain():
    service = EcobeeService("test", "a" * 32)

    assert isinstance(service._authorization, AuthorizationService)
    assert isinstance(service._thermostats, ThermostatsService)
    assert isinstance(service._groups, GroupsService)
    assert isinstance(service._hierarchy, HierarchyService)
    assert isinstance(service._demand, DemandService)
    assert isinstance(service._reports, ReportsService)


def test_facade_method_signatures_match_master():
    baseline = subprocess.run(
        ["git", "show", "master:pyecobee/service.py"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    def public_method_arguments(source):
        service_class = next(
            node
            for node in ast.parse(source).body
            if isinstance(node, ast.ClassDef) and node.name == "EcobeeService"
        )
        return {
            node.name: ast.dump(node.args)
            for node in service_class.body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        }

    assert public_method_arguments(Path("pyecobee/service.py").read_text()) == (
        public_method_arguments(baseline)
    )
