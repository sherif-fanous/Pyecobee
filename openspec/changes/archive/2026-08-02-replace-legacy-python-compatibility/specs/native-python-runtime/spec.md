## Purpose

Defines the native Python 3.12 runtime behavior used by Pyecobee after removing compatibility layers for unsupported Python versions.

## ADDED Requirements

### Requirement: Text inputs use str
Public text inputs and text-valued model fields SHALL use Python `str` semantics and SHALL reject non-string values according to the existing validation contract.

#### Scenario: Valid text input is accepted
- **WHEN** a public API receives a Python str value
- **THEN** it processes the value normally

### Requirement: Datetimes are timezone-aware where required
Report APIs that operate on dates and times SHALL require timezone-aware datetime values and SHALL normalize accepted aware values consistently for API requests.

#### Scenario: Naive report datetime is provided
- **WHEN** a report method receives a naive datetime
- **THEN** it raises a clear validation error before making an HTTP request

### Requirement: Standard library compatibility is sufficient
The runtime package SHALL not require six, enum34, or pytz for supported Python versions.

#### Scenario: Runtime dependencies are inspected
- **WHEN** the package is installed on Python 3.12
- **THEN** native enum, datetime, and string functionality is used without those compatibility packages
