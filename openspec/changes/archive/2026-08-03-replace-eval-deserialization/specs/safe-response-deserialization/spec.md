## Purpose

Converts ecobee JSON responses into Pyecobee objects through explicit type information and recursive construction without executing generated Python source.

## ADDED Requirements

### Requirement: Deserialization does not evaluate payload-generated code
The response conversion path SHALL NOT use eval, exec, or generated Python source to construct response objects.

#### Scenario: Normal nested response is converted
- **WHEN** a valid response contains nested objects and lists
- **THEN** the expected object graph is created through direct construction

### Requirement: Known fields retain their types
Supported model fields SHALL preserve existing conversions for primitive values, enums, optional values, nested objects, and lists.

#### Scenario: Nested list response is converted
- **WHEN** a known response contains a list of supported objects
- **THEN** each list entry is converted to the declared model type

### Requirement: Unknown API additions are handled predictably
Unknown fields and unsupported nested API objects SHALL follow a documented compatibility policy and SHALL NOT corrupt sibling fields or crash otherwise valid responses.

#### Scenario: Unsupported nested object is present
- **WHEN** a supported response contains a newly introduced unsupported object
- **THEN** the response follows the documented skip or preservation behavior and records a diagnostic

### Requirement: Malformed known data has a clear error
The converter SHALL raise a library-level error containing the affected field or model when known data cannot be converted.

#### Scenario: Known field has an invalid shape
- **WHEN** a known object field receives incompatible JSON data
- **THEN** conversion fails with a clear typed error identifying the field or model
