## Context

`EcobeeService` calls module-level requests functions repeatedly, while `Utilities.make_http_request` combines logging, transport, and exception conversion. Logs include all headers and JSON values.

## Goals / Non-Goals

**Goals:**
- Add a session-backed internal transport.
- Preserve endpoint and exception behavior.
- Redact secrets by default.
- Make transport easy to mock.

**Non-Goals:**
- Change the external requests library.
- Redesign public service method names.
- Add retries or rate limiting unless required to preserve current behavior.

## Decisions

Use `requests.Session` behind a small internal transport interface. Keep timeout values explicit at the public boundary and pass them to every request. Parse response JSON once in the transport/response-processing path. Redact by semantic header and credential field names rather than trying to scrub arbitrary strings after logging.

## Risks / Trade-offs

- [Risk] A transport extraction changes subtle request parameters. → Assert URL, method, headers, query/body, and timeout for representative methods before migrating all calls.
- [Risk] Redaction makes debugging harder. → Preserve safe metadata and response diagnostics while never exposing secrets.
