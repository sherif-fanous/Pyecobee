# response-contract-testing Specification

## Purpose

Protects Pyecobee's public request, response, serialization, validation, and exception behavior with deterministic tests before internal refactors are applied.

## Requirements

### Requirement: Public response contracts are tested
Representative successful responses SHALL be tested for authorization, tokens, thermostats, groups, hierarchy, runtime reports, and meter reports.

#### Scenario: Representative fixture is processed
- **WHEN** a supported fixture is passed through the public response processing path
- **THEN** the expected response type and important nested values are asserted

### Requirement: Error contracts are tested
The suite SHALL test authorization errors, ecobee API status errors, generic HTTP errors, request exceptions, malformed JSON, and invalid argument validation.

#### Scenario: HTTP failure is processed
- **WHEN** a mocked response represents an ecobee error
- **THEN** the documented typed exception and relevant error details are produced

### Requirement: Tests enforce coverage visibility
The documented test command SHALL make coverage results visible and SHALL define a maintainable initial coverage threshold.

#### Scenario: Coverage command runs
- **WHEN** the documented coverage command is executed
- **THEN** it reports line coverage for production modules and fails below the configured baseline
