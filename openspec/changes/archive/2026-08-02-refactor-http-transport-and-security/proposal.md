## Why

HTTP behavior is repeated throughout the 3,100-line service and debug logging currently risks exposing bearer tokens and other credentials. Centralizing transport improves testability, consistency, and security without requiring an immediate public API redesign.

## What Changes

- Introduce an internal session-backed HTTP transport boundary.
- Centralize headers, timeout handling, JSON decoding, and exception conversion.
- Preserve existing Ecobee exception types and public service methods.
- **BREAKING**: Redact authorization and credential values from logs.
- Add tests proving secrets never appear in request logs.

## Capabilities

### New Capabilities
- `secure-http-transport`: Defines consistent and safe outbound HTTP behavior.

### Modified Capabilities

## Impact

Affects `EcobeeService`, `Utilities`, request mocking, logging, and tests. It should preserve endpoint URLs, payloads, public method names, and exception classes.
