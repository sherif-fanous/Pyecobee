## 0. Branch and scope

- [x] 0.1 Create `chore/establish-modernization-baseline` from the current `master` branch using `git switch -c chore/establish-modernization-baseline` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Test setup

- [x] 1.1 Add pytest and pytest-cov as development dependencies through the project tooling.
- [x] 1.2 Add pytest configuration and a documented default test command.
- [x] 1.3 Separate or mark the existing live integration script so default collection cannot execute it.

## 2. Fixtures and coverage

- [x] 2.1 Inventory existing response fixtures and copy representative payloads into a stable fixture directory.
- [x] 2.2 Add import and package smoke tests.
- [x] 2.3 Add offline tests for representative successful response deserialization.
- [x] 2.4 Add offline tests for authorization, API, HTTP, and requests error paths.
- [x] 2.5 Add tests for unsupported nested API objects and malformed response shapes.
- [x] 2.6 Add tests for current service argument validation and date handling.

## 3. Verification

- [x] 3.1 Verify the default suite completes without credentials or network access.
- [x] 3.2 Document how to run opt-in live integration tests.
- [x] 3.3 Record the baseline command and result for the next modernization change.
