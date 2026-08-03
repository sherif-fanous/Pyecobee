## Why

`pyecobee/service.py` contains more than 3,000 lines and combines authorization, transport calls, thermostat operations, reports, groups, hierarchy, and demand APIs. This slows review and makes domain changes risky.

## What Changes

- **BREAKING**: Introduce domain-oriented internal service components.
- Preserve an `EcobeeService` facade for existing method names during migration.
- Separate authorization, thermostats, groups, hierarchy, demand, and reports.
- Add explicit public import boundaries instead of relying on wildcard imports.

## Capabilities

### New Capabilities

- `domain-oriented-client`: Provides maintainable domain boundaries while preserving the compatibility facade during migration.

### Modified Capabilities

## Impact

Affects service module organization, package exports, dependency injection, and internal tests. Endpoint behavior and existing facade methods remain compatible unless explicitly documented in the 2.0 migration notes.
