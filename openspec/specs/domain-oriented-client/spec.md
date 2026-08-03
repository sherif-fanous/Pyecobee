# domain-oriented-client Specification

## Purpose

Organizes the ecobee client by API domain while keeping a compatibility facade so consumers can migrate incrementally.

## Requirements

### Requirement: Domain operations have clear boundaries
Authorization, thermostat, group, hierarchy, demand, and report operations SHALL be implemented behind distinct domain boundaries.

#### Scenario: Domain operation is invoked
- **WHEN** a caller performs a thermostat or report operation
- **THEN** the operation is routed through its corresponding domain component without changing endpoint behavior

### Requirement: Existing facade remains available
The existing EcobeeService entry point and documented method names SHALL remain available during the domain split.

#### Scenario: Existing consumer imports the service
- **WHEN** an existing consumer imports and constructs EcobeeService
- **THEN** construction and existing method dispatch continue to work

### Requirement: Package exports are explicit
The package SHALL expose a documented explicit public surface rather than requiring wildcard imports.

#### Scenario: Consumer follows documented imports
- **WHEN** a consumer imports documented service, model, enum, or exception names
- **THEN** those names are available without importing unrelated implementation symbols
