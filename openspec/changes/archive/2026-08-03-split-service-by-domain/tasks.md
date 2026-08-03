## 0. Branch and scope

- [x] 0.1 Create `chore/split-service-by-domain` from the current `master` branch using `git switch -c chore/split-service-by-domain` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Domain boundaries

- [x] 1.1 Inventory EcobeeService methods by API domain.
- [x] 1.2 Create shared client context and domain component interfaces.
- [x] 1.3 Extract authorization and thermostat operations.
- [x] 1.4 Extract groups, hierarchy, demand, and report operations.

## 2. Compatibility facade

- [x] 2.1 Delegate existing EcobeeService methods to domain components.
- [x] 2.2 Preserve signatures, return types, and exception behavior.
- [x] 2.3 Add explicit package exports and documented import examples.

## 3. Verification

- [x] 3.1 Run existing facade contract tests for each domain.
- [x] 3.2 Verify no circular imports or wildcard-only public imports remain.
- [x] 3.3 Update migration documentation with any intentional breaking changes.
