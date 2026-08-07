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
