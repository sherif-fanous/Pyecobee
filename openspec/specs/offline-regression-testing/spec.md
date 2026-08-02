# offline-regression-testing Specification

## Purpose

Provides deterministic automated coverage that protects Pyecobee behavior while the packaging, compatibility, transport, and deserialization layers are modernized.

## Requirements

### Requirement: Default tests are offline
The default test command SHALL run without ecobee credentials, network access, or thermostat mutation.

#### Scenario: Developer runs the test suite locally
- **WHEN** the developer runs the documented pytest command in a clean environment
- **THEN** tests use local fixtures and mocks and do not require credentials

### Requirement: Representative API behavior is covered
The test suite SHALL cover representative authorization, thermostat, group, hierarchy, report, success, and error response shapes.

#### Scenario: Response fixture is deserialized
- **WHEN** a representative JSON fixture is processed
- **THEN** the expected response object and nested fields are asserted

### Requirement: Live tests are opt-in
Any test that contacts ecobee SHALL be explicitly marked and excluded from the default test command.

#### Scenario: Credentials are absent
- **WHEN** the default test suite runs without live-test environment variables
- **THEN** no live integration test is attempted
