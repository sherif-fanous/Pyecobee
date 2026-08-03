## 0. Branch and scope

- [x] 0.1 Create `chore/refactor-http-transport-and-security` from the current `master` branch using `git switch -c chore/refactor-http-transport-and-security` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Transport boundary

- [x] 1.1 Define the internal session-backed transport interface.
- [x] 1.2 Centralize default headers, timeout propagation, response decoding, and request exception conversion.
- [x] 1.3 Migrate representative service methods and remove duplicated request setup.
- [x] 1.4 Migrate remaining service methods and preserve public signatures.

## 2. Secure diagnostics

- [x] 2.1 Implement header and JSON-field redaction for credentials.
- [x] 2.2 Update request and response logging to use redacted data.
- [x] 2.3 Add tests asserting bearer tokens and credential values never appear in logs.

## 3. Verification

- [x] 3.1 Assert transport method, URL, payload, headers, and timeout for representative calls.
- [x] 3.2 Run all offline regression tests and Ruff checks.
- [x] 3.3 Verify typed exceptions and chained causes for network failures.
