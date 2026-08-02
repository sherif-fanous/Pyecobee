## Why

Pyecobee currently has no dependable offline regression suite: `tests/test.py` is a manually-run live integration script. Modernization work needs a behavioral baseline before changing packaging, compatibility code, transport, or deserialization.

## What Changes

- **BREAKING**: Make automated tests the default verification path instead of the live script.
- Add representative JSON fixtures and import/build smoke coverage.
- Define an explicit opt-in boundary for live ecobee integration tests.
- Record current public API and response behavior needed by later changes.

## Capabilities

### New Capabilities

- `offline-regression-testing`: Provides deterministic, credential-free regression coverage for current library behavior.

### Modified Capabilities

## Impact

Adds pytest development tooling and test fixtures under `tests/`. It does not change the runtime API or production dependencies. The existing live script is retained as opt-in documentation until a later cleanup change.
