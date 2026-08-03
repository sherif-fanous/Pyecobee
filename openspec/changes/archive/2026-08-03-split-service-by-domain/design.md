## Context

The transport and deserializer changes establish testable internals. The service still combines all API domains and the package root imports nearly every symbol explicitly for wildcard use.

## Goals / Non-Goals

**Goals:**

- Create domain modules with a shared client/transport dependency.
- Keep EcobeeService as a delegating facade.
- Define explicit package exports.

**Non-Goals:**

- Introduce an entirely new client API in the same change.
- Change endpoint payloads or authentication flow.
- Remove facade methods without a deprecation period.

## Decisions

Use composition and delegation rather than inheritance. Domain components receive the shared transport, serializer, and authentication context. Keep method names on EcobeeService as thin delegates. Add `__all__` and documented direct import paths; retain compatibility aliases only where needed.

## Risks / Trade-offs

- [Risk] Delegation can subtly alter method binding or exceptions. → Use contract tests against the existing facade.
- [Risk] Splitting files creates circular imports. → Keep domain components dependent on narrow shared protocols and avoid importing the package root.
