## 0. Branch and scope

- [x] 0.1 Create `chore/adopt-ruff-tooling` from the current `master` branch using `git switch -c chore/adopt-ruff-tooling` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Configuration

- [x] 1.1 Add Ruff configuration to pyproject.toml with Python 3.12 target and artifact exclusions.
- [x] 1.2 Add documented `uv run ruff check .` and `uv run ruff format --check .` commands.
- [x] 1.3 Update editor configuration to use Ruff and remove obsolete formatter/linter settings.

## 2. Source cleanup

- [x] 2.1 Run Ruff import sorting and safe autofixes.
- [x] 2.2 Format production and test Python files with Ruff.
- [x] 2.3 Resolve remaining lint findings or document narrow justified ignores.
- [x] 2.4 Retire obsolete pylint configuration and references.

## 3. Verification

- [x] 3.1 Verify Ruff check and format check pass from a clean uv environment.
- [x] 3.2 Verify the offline regression suite passes after formatting.
- [x] 3.3 Review the diff to confirm no intentional behavior change was introduced.
