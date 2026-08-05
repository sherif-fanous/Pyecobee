## Why

The object model contains extensive repetitive property code, `__slots__`, string-based type metadata, and hand-maintained field maps. Once deserialization behavior is protected, the model layer can become clearer, more typed, and easier to extend.

## What Changes

- **BREAKING**: Replace or simplify repetitive model boilerplate with Pydantic v2 models.
- Define explicit API aliases, optional fields, nested models, and enum handling.
- Add Pydantic as a runtime dependency and document its model behavior.
- Preserve readable representations and predictable serialization.
- Choose standard-library dataclasses or a validation library based on measured needs.

## Capabilities

### New Capabilities

- `typed-object-model`: Provides explicit typed request and response models with stable API field mapping.

### Modified Capabilities

## Impact

Affects nearly all files under `pyecobee/objects`, response classes, constructors, serialization, and consumer code. This is intentionally later than the packaging and safety work and may warrant a separate major release.
