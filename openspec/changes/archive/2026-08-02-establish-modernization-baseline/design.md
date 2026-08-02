## Context

The repository contains a large live script in `tests/test.py`, several captured response files, and no pytest configuration. Later changes need repeatable checks around nested object conversion and service validation.

## Goals / Non-Goals

**Goals:**

- Establish an offline pytest entry point.
- Preserve representative response payloads as fixtures.
- Make live tests explicit and opt-in.

**Non-Goals:**

- Refactor production models.
- Change the public API.
- Add broad code-quality tooling; that belongs to a separate change.

## Decisions

Use pytest with mocked HTTP responses and local JSON fixtures. This is preferable to relying on the current live script because failures remain reproducible and CI-safe. Keep the live script temporarily, but mark or relocate it so it cannot be collected by the default suite.

Start with high-value response and error paths rather than attempting exhaustive coverage of every API method in one change.

## Risks / Trade-offs

- [Risk] Existing fixtures may represent old ecobee payloads. → Keep them as regression fixtures and add focused synthetic payloads for current edge cases.
- [Risk] Tests may accidentally make network calls. → Use mocks and a test-level network guard where practical.
