## Purpose

Defines a reproducible Python 3.12+ package and development environment for installing, testing, building, and releasing Pyecobee.

## ADDED Requirements

### Requirement: Python 3.12 is the minimum
The package metadata SHALL reject Python versions older than 3.12 and SHALL advertise supported Python 3.12+ classifiers.

#### Scenario: Package metadata is inspected
- **WHEN** the built distribution metadata is read
- **THEN** it declares `Requires-Python: >=3.12`

### Requirement: uv is the dependency workflow
The repository SHALL declare runtime and development dependencies in pyproject.toml and SHALL commit uv.lock for reproducible environments.

#### Scenario: Locked environment is synchronized
- **WHEN** a developer runs `uv sync --locked`
- **THEN** dependencies are installed without reading requirements.txt

### Requirement: The package remains buildable
The project SHALL produce installable source and wheel distributions using the configured PEP 517 build backend.

#### Scenario: Distribution is built
- **WHEN** `uv build` is run
- **THEN** source and wheel artifacts are produced and the wheel can be installed in a Python 3.12 environment
