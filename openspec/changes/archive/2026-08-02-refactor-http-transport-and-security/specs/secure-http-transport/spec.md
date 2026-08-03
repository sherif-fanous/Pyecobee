## Purpose

Provides one testable HTTP boundary that consistently handles sessions, timeouts, response decoding, typed errors, and protection of credentials in diagnostic output.

## ADDED Requirements

### Requirement: Requests use bounded transport
All outbound API calls SHALL use the centralized transport boundary and SHALL receive a bounded timeout.

#### Scenario: Service method sends a request
- **WHEN** a public service operation performs HTTP I/O
- **THEN** it uses the shared transport and passes the configured timeout

### Requirement: Credentials are redacted
Diagnostic logs SHALL redact bearer tokens, authorization codes, refresh tokens, application keys, and other configured secrets.

#### Scenario: Request logging is enabled
- **WHEN** a request contains an Authorization header or credential payload
- **THEN** the secret value does not appear in emitted logs

### Requirement: Request exceptions are typed
Transport-level requests exceptions SHALL be converted into `EcobeeRequestsException` while retaining the original exception as its cause.

#### Scenario: Network request fails
- **WHEN** the underlying HTTP library raises a transport exception
- **THEN** callers receive `EcobeeRequestsException` with chained cause information
