## 0. Branch and scope

- [x] 0.1 Create `chore/replace-legacy-python-compatibility` from the current `master` branch using `git switch -c chore/replace-legacy-python-compatibility` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Remove compatibility dependencies

- [x] 1.1 Replace six string checks and type names with native str behavior.
- [x] 1.2 Replace six.reraise with native exception chaining.
- [x] 1.3 Remove enum34 declarations and compatibility comments.
- [x] 1.4 Replace pytz UTC and named-zone usage with datetime.UTC and zoneinfo.

## 2. Runtime cleanup

- [x] 2.1 Replace old-style super calls and Python 2-only branches.
- [x] 2.2 Make naive datetime rejection explicit for report methods.
- [x] 2.3 Update tests, fixtures, and documentation examples.
- [x] 2.4 Remove now-unused runtime imports and dependency declarations.

## 3. Verification

- [x] 3.1 Search the repository for six, enum34, pytz, and Python 2 compatibility references.
- [x] 3.2 Run offline tests and Ruff checks.
- [x] 3.3 Verify report request validation and exception behavior remain covered.
