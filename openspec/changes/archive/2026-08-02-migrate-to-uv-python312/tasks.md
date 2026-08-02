## 0. Branch and scope

- [x] 0.1 Create `chore/migrate-to-uv-python312` from the current `master` branch using `git switch -c chore/migrate-to-uv-python312` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Packaging metadata

- [x] 1.1 Create pyproject.toml with project metadata, Python >=3.12, package discovery, and build configuration.
- [x] 1.2 Move runtime and development dependencies into pyproject.toml.
- [x] 1.3 Remove setup.py and requirements.txt after equivalent metadata is verified.
- [x] 1.4 Generate and commit uv.lock.

## 2. Environment and documentation

- [x] 2.1 Update the devcontainer to use Python 3.12 or newer and uv.
- [x] 2.2 Update README and history with Python 3.12+ installation instructions.
- [x] 2.3 Remove obsolete Python classifiers and compatibility dependency declarations.

## 3. Verification

- [x] 3.1 Run `uv sync --locked` in a clean environment.
- [x] 3.2 Build and install both wheel and source distributions.
- [x] 3.3 Verify package import and the baseline test suite.
