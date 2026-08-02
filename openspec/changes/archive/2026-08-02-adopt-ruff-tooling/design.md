## Context

The codebase is large and consistently formatted by older conventions, but it has no pyproject tooling configuration. A formatter-only diff should be isolated from behavior changes.

## Goals / Non-Goals

**Goals:**

- Configure Ruff for Python 3.12.
- Normalize imports and formatting.
- Make checks easy to run locally and in CI.

**Non-Goals:**

- Fix every architectural lint finding in this change.
- Add type checking.
- Refactor production behavior.

## Decisions

Use Ruff for formatting, linting, and import sorting rather than retaining Black plus a separate import tool. Start with safe rules (syntax, pyflakes, imports, modernization, common bug patterns) and add stricter rules only after the baseline is green. Review the formatter diff separately from semantic changes.

## Risks / Trade-offs

- [Risk] Ruff exposes many pre-existing findings. → Fix mechanical findings in this change and track intentional exceptions narrowly.
- [Risk] Formatting creates a large diff. → Keep this as a standalone commit/change and do not mix it with behavior refactors.
