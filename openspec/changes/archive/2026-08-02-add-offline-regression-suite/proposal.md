## Why

The baseline suite establishes the test harness, but modernization requires broader coverage before changing HTTP transport and deserialization. The current manual tests do not cover failure paths or protect against regressions offline.

## What Changes

- Expand fixture-driven pytest coverage across public response and service behavior.
- Add mocked transport tests for request construction and timeout propagation.
- Add serialization, validation, enum, datetime, and unknown-object cases.
- Add coverage reporting and a practical minimum threshold.

## Capabilities

### New Capabilities

- `response-contract-testing`: Provides broad deterministic coverage of the public API response and validation contract.

### Modified Capabilities

## Impact

Adds tests and fixtures only, with pytest-cov as development tooling. This change should expose behavior that later transport and serializer changes must preserve.
