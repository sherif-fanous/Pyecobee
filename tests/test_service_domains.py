import ast
import subprocess
from pathlib import Path

from pyecobee.services import (
    AuthorizationService,
    DemandService,
    GroupsService,
    HierarchyService,
    ReportsService,
    ThermostatsService,
)
from tests.support import build_service


def test_facade_uses_a_component_for_each_api_domain():
    service = build_service()

    assert isinstance(service._authorization, AuthorizationService)
    assert isinstance(service._thermostats, ThermostatsService)
    assert isinstance(service._groups, GroupsService)
    assert isinstance(service._hierarchy, HierarchyService)
    assert isinstance(service._demand, DemandService)
    assert isinstance(service._reports, ReportsService)


def test_api_operation_signatures_match_the_last_release():
    """Version 2 redesigns how credentials are held, not how requests are made."""

    baseline = subprocess.run(
        ["git", "show", "v1.3.13:pyecobee/service.py"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    class NormalizeSelectionTypeValue(ast.NodeTransformer):
        def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
            self.generic_visit(node)
            if (
                node.attr == "value"
                and isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "SelectionType"
            ):
                return node.value
            return node

    def api_operation_arguments(source):
        tree = NormalizeSelectionTypeValue().visit(ast.parse(source))
        service_class = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "EcobeeService"
        )
        return {
            node.name: ast.dump(node.args)
            for node in service_class.body
            if isinstance(node, ast.FunctionDef)
            and not node.name.startswith("_")
            # Properties are excluded: credentials are now a Tokens value
            # object rather than a set of individually assignable attributes.
            and not node.decorator_list
        }

    current = api_operation_arguments(Path("pyecobee/service.py").read_text())
    baseline_operations = api_operation_arguments(baseline)

    # Operations may be added, but every operation released in 1.3.13 must keep
    # its signature so that existing callers continue to work.
    assert {
        name: arguments
        for name, arguments in current.items()
        if name in baseline_operations
    } == baseline_operations
