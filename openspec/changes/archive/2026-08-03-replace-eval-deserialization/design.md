## Context

`Utilities.dictionary_to_object` currently builds source fragments using string metadata and evaluates them. Class discovery is also performed dynamically through the utilities module. Existing behavior includes skipping unsupported nested object definitions after the recent bug fix.

## Goals / Non-Goals

**Goals:**

- Remove eval and generated source.
- Preserve successful response object shapes.
- Make model registration and field conversion explicit.
- Make unknown and malformed data behavior testable.

**Non-Goals:**

- Convert every model to dataclasses in this change.
- Add a third-party validation framework.
- Change endpoint payload formats.

## Decisions

Implement a recursive converter driven by an explicit registry and field metadata. Resolve API field names to model constructor names, then recursively convert dictionaries, lists, enums, and primitives. Start with the existing classes to reduce migration scope; simplify metadata in a later object-model change once behavior is stable.

Unknown scalar fields will be ignored with diagnostics. Unsupported nested objects will be skipped according to the current compatibility intent, but the converter must preserve processing of sibling fields. Known conversion failures will raise a dedicated or existing library exception with field context.

## Risks / Trade-offs

- [Risk] The legacy metadata contains inconsistencies that eval previously masked. → Migrate one response family at a time and use fixture tests as the acceptance gate.
- [Risk] Skipping unknown objects can lose data. → Log structured diagnostics and document the policy; consider an opt-in raw-preservation mode later.
