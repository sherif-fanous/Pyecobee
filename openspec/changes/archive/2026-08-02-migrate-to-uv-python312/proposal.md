## Why

The project still uses setup.py, requirements.txt, Python 2-era classifiers, and ad hoc pip installation. A Python 3.12+ baseline and locked uv environment are prerequisites for reliable modernization.

## What Changes

- **BREAKING**: Raise minimum Python version to 3.12.
- Replace setup.py metadata with pyproject.toml.
- Replace requirements.txt with project dependencies and a committed uv.lock.
- Remove enum34, six, and pytz from runtime dependencies where no longer needed.
- Update devcontainer and installation documentation.

## Capabilities

### New Capabilities

- `modern-python-packaging`: Defines the supported Python and reproducible package environment contract.

### Modified Capabilities

## Impact

Affects setup.py, requirements.txt, devcontainer files, package metadata, installation documentation, and release versioning. This is a deliberate version-2 breaking change.
