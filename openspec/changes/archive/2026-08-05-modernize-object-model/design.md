## Context

This change follows the safe deserializer and regression suite. The current classes are repetitive and rely on `__slots__`, properties, and string metadata.

## Goals / Non-Goals

**Goals:**

- Reduce repetitive model boilerplate.
- Make types, aliases, and nested structures explicit.
- Preserve JSON request/response compatibility.

**Non-Goals:**

- Begin before the current behavior is protected by fixtures.
- Change ecobee endpoint semantics.
- Add a dependency without comparing it to dataclasses and the existing approach.

## Decisions

Use Pydantic v2 as the model and validation layer. The project has dozens of nested request and response models, API field aliases, enum conversion, optional fields, and unknown ecobee fields. Pydantic provides these capabilities directly and avoids recreating a custom validation and serialization framework with dataclasses.

Configure response models to ignore unknown fields by default so newer ecobee response fields remain forward-compatible. Configure request models more strictly, rejecting unsupported fields where appropriate. Use `populate_by_name=True` where consumers need Python field names while serialization uses ecobee aliases. Use `model_dump(by_alias=True, exclude_none=True)` for outgoing payloads.

Migrate one representative model family first, then expand using contract tests. Preserve compatibility aliases and readable representations where practical, but treat constructor and validation changes as documented version-2 behavior.

## Risks / Trade-offs

- [Risk] Constructor and mutability changes break consumers. → Publish a migration table and retain compatibility aliases where inexpensive.
- [Risk] Strict validation rejects previously tolerated API data. → Separate strict request models from tolerant response models and test real fixtures.
- [Risk] Pydantic adds runtime weight and dependency surface. → Pin a supported Pydantic v2 range, keep the public API model-oriented rather than exposing Pydantic internals unnecessarily, and verify wheel installation in CI.
