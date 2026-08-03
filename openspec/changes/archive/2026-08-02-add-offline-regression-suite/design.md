## Context

The first baseline change creates the harness. This change expands it around the highest-risk utility and service paths, using mocked requests and existing API payloads.

## Goals / Non-Goals

**Goals:**

- Cover public behavior needed by transport and deserializer refactors.
- Make error and validation behavior explicit.
- Introduce visible coverage without chasing an arbitrary high percentage.

**Non-Goals:**

- Test every generated model property exhaustively.
- Contact the ecobee service.
- Change production implementation.

## Decisions

Prefer public entry points and fixture-backed tests over tests coupled to private helpers. Use a fake or mocked requests session so request method, URL, headers, body, and timeout can be asserted without network access. Establish a modest baseline and raise it as refactors land.

## Risks / Trade-offs

- [Risk] Fixture tests can overfit old payloads. → Combine real captured fixtures with focused synthetic edge-case payloads.
- [Risk] Coverage percentage can encourage low-value tests. → Prioritize behavior and use the threshold as a floor, not the goal.
