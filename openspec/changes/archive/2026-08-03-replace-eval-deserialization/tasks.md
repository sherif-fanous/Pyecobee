## 0. Branch and scope

- [x] 0.1 Create `chore/replace-eval-deserialization` from the current `master` branch using `git switch -c chore/replace-eval-deserialization` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Converter foundation

- [x] 1.1 Inventory current model registry, API field maps, and type metadata.
- [x] 1.2 Define explicit model registration and field-resolution helpers.
- [x] 1.3 Implement recursive conversion for primitives, enums, optional values, dictionaries, and lists.
- [x] 1.4 Add contextual typed errors for malformed known fields.

## 2. Migration

- [x] 2.1 Migrate authorization, token, status, and error response families.
- [x] 2.2 Migrate thermostat, group, hierarchy, and report response families.
- [x] 2.3 Preserve unsupported-object diagnostics and sibling-field processing.
- [x] 2.4 Remove generated-source construction and all eval/exec calls from production deserialization.

## 3. Verification

- [x] 3.1 Run fixture tests for every migrated response family.
- [x] 3.2 Add regression tests for unknown fields, unsupported nested objects, empty lists, and malformed data.
- [x] 3.3 Run Ruff, coverage, package build, and the complete offline suite.
