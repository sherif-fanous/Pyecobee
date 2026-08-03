## Why

The current deserializer generates Python source and calls eval() to construct response objects. This is difficult to reason about, tightly coupled to string metadata, and creates avoidable security and maintenance risk when API payloads evolve.

## What Changes

- **BREAKING**: Replace generated-source/eval deserialization with direct recursive construction.
- Introduce explicit model/type registration and field mapping.
- Preserve nested objects, lists, enums, optional fields, and primitive values.
- Define and test behavior for unknown fields and unsupported nested objects.
- Produce clear typed errors for malformed known data.

## Capabilities

### New Capabilities

- `safe-response-deserialization`: Provides deterministic, non-evaluating conversion from ecobee JSON to library response objects.

### Modified Capabilities

## Impact

Affects `pyecobee.utilities`, all response/model metadata, error behavior, and fixture tests. This is an internal implementation replacement with intentionally documented edge-case behavior; response object types and normal public results should remain compatible.
