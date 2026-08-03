## 0. Branch and scope

- [x] 0.1 Create `chore/add-offline-regression-suite` from the current `master` branch using `git switch -c chore/add-offline-regression-suite` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Fixture coverage

- [x] 1.1 Add fixture loaders and reusable mocked response helpers.
- [x] 1.2 Add success-path tests for representative response families.
- [x] 1.3 Add nested lists, optional fields, enum values, and primitive list tests.

## 2. Failure and validation coverage

- [x] 2.1 Add authorization, API status, HTTP, request, and malformed JSON tests.
- [x] 2.2 Add request method, URL, headers, payload, and timeout assertions.
- [x] 2.3 Add invalid argument and date-boundary tests.
- [x] 2.4 Add unknown fields and unsupported nested-object tests.

## 3. Coverage workflow

- [x] 3.1 Add pytest-cov configuration and a documented coverage command.
- [x] 3.2 Set and record an initial realistic coverage threshold.
- [x] 3.3 Verify tests remain offline and pass under the locked uv environment.
