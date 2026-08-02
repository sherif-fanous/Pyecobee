## Why

The repository has no current automated formatter or linter workflow and contains legacy editor configuration for pylint and multiple formatters. Ruff provides one fast, centrally configured tool for formatting, imports, and linting.

## What Changes

- Add Ruff configuration to pyproject.toml targeting Python 3.12.
- Format the source tree and normalize imports.
- Add lint and format commands through uv.
- **BREAKING**: Retire pylint and any Black/autopep8/yapf workflow as supported project tooling.
- Add editor guidance and CI-ready checks.

## Capabilities

### New Capabilities

- `ruff-code-quality`: Defines the repository's formatting and linting contract.

### Modified Capabilities

## Impact

Affects pyproject.toml, source formatting, editor configuration, legacy lint configuration, and future contribution workflows. Runtime behavior should not change.
