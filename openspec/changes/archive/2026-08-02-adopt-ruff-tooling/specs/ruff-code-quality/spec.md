## Purpose

Provides one deterministic formatting and linting workflow for maintaining Python 3.12-compatible source code and imports.

## ADDED Requirements

### Requirement: Ruff owns formatting

The project SHALL configure Ruff formatting in pyproject.toml and SHALL keep all tracked Python source formatted by Ruff.

#### Scenario: Format check runs

- **WHEN** `uv run ruff format --check .` is executed
- **THEN** it reports no formatting changes required

### Requirement: Ruff owns linting and imports

The project SHALL use Ruff for the configured lint rules and import sorting, including detection of unused imports and Python-version modernization opportunities where enabled.

#### Scenario: Lint check runs

- **WHEN** `uv run ruff check .` is executed
- **THEN** it completes successfully for tracked production and test source

### Requirement: Generated and build artifacts are excluded

Ruff checks SHALL exclude build, distribution, virtual environment, and generated PlantUML artifacts.

#### Scenario: Tooling runs from the repository root

- **WHEN** Ruff is invoked against `.`
- **THEN** ignored generated artifacts do not create lint or formatting failures
