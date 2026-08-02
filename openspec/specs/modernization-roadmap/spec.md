## Purpose

Defines the target architecture, tooling baseline, migration sequence, and completion criteria for modernizing Pyecobee while explicitly raising the minimum supported Python version to 3.12.

## Requirements

### Requirement: Python and packaging baseline

The project SHALL support Python 3.12 and newer only, SHALL declare `requires-python = ">=3.12"`, SHALL use `pyproject.toml` for package metadata and build configuration, and SHALL use uv with a committed lockfile for dependency management.

#### Scenario: Reproducible development environment

- **WHEN** a developer runs `uv sync --locked` on Python 3.12 or newer
- **THEN** the project environment is created from the committed lockfile and the package can be imported

#### Scenario: Legacy dependency files are absent

- **WHEN** the repository is inspected after the packaging migration
- **THEN** `setup.py`, `requirements.txt`, and Python 2 compatibility dependencies are no longer required

### Requirement: Unified code quality tooling

The project SHALL use Ruff for linting, import sorting, and formatting, with configuration stored in `pyproject.toml` and checks runnable through uv.

#### Scenario: Formatting is enforced

- **WHEN** CI runs the formatting check
- **THEN** `uv run ruff format --check .` succeeds

#### Scenario: Linting is enforced

- **WHEN** CI runs the lint check
- **THEN** `uv run ruff check .` succeeds

### Requirement: Offline regression coverage

The project SHALL provide automated offline tests for serialization, service validation, HTTP error handling, representative API responses, and unsupported response objects.

#### Scenario: Normal test execution does not contact ecobee

- **WHEN** a developer runs the default test command without credentials
- **THEN** tests complete without network access or mutation of a real thermostat

#### Scenario: Live integration tests are opt-in

- **WHEN** live ecobee tests are present
- **THEN** they are explicitly marked and excluded from the default CI test run

### Requirement: Safe HTTP behavior

The client SHALL centralize HTTP transport behavior, use bounded request timeouts, preserve typed ecobee exceptions, and SHALL NOT log bearer tokens, authorization codes, refresh tokens, or application keys.

#### Scenario: Sensitive request data is logged safely

- **WHEN** debug logging is enabled for a request containing an authorization header
- **THEN** the log output redacts the secret value

#### Scenario: Transport failures remain typed

- **WHEN** the HTTP client raises a requests transport exception
- **THEN** the library raises an `EcobeeRequestsException` with the original exception chained

### Requirement: Safe response deserialization

The client SHALL deserialize JSON responses without evaluating generated Python source and SHALL handle unknown API fields or unsupported nested objects according to a documented compatibility policy.

#### Scenario: Unsupported nested object does not crash a response

- **WHEN** an otherwise valid response contains an unsupported nested API object
- **THEN** deserialization completes according to the documented skip or preservation policy and records diagnostic information

#### Scenario: Malformed known data fails clearly

- **WHEN** a known response field has an invalid shape or type
- **THEN** deserialization raises a clear library error rather than an arbitrary evaluation or attribute error

### Requirement: Public API migration

The project SHALL document the Python 3.12-only support policy, dependency/tooling migration, and any intentional version-2 breaking changes before release.

#### Scenario: Consumer can find migration guidance

- **WHEN** a consumer reads the README or release history
- **THEN** they can identify supported Python versions, installation commands, removed compatibility dependencies, and relevant API changes

## Delivery Sequence

Implementation changes SHALL be delivered in this order:

1. Establish the modernization baseline and test fixtures.
2. Migrate packaging and dependency management to uv and Python 3.12+.
3. Adopt Ruff as the formatter and linter.
4. Remove Python 2 compatibility code and replace pytz with zoneinfo.
5. Expand the offline regression suite.
6. Refactor HTTP transport and redact sensitive logs.
7. Replace eval-based deserialization.
8. Optionally split the service and modernize the object model after behavior is protected.
9. Add CI, documentation, and release automation.

Each logical change SHALL leave the repository buildable and testable.
