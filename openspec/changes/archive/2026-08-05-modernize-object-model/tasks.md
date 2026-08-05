## 0. Branch and scope

- [x] 0.1 Create `chore/modernize-object-model` from the current `master` branch using `git switch -c chore/modernize-object-model` after synchronizing the branch with `git pull --ff-only`.
- [x] 0.2 Implement only this OpenSpec change on the branch; do not mix work from later modernization changes.
- [x] 0.3 Run the change's tests and OpenSpec validation before considering the implementation complete.

## 1. Pydantic model strategy

- [x] 1.1 Add a supported Pydantic v2 runtime dependency.
- [x] 1.2 Inventory model fields, ecobee aliases, constructors, and nested relationships.
- [x] 1.3 Define strict request-model and tolerant response-model configuration.
- [x] 1.4 Define model compatibility and migration rules, including constructor and validation changes.

## 2. Incremental migration

- [x] 2.1 Migrate one representative request and response family to Pydantic v2.
- [x] 2.2 Implement explicit aliases, nested conversion, enum handling, and `model_dump(by_alias=True, exclude_none=True)` serialization.
- [x] 2.3 Configure unknown-field handling so response models tolerate newer ecobee fields while request models reject unsupported fields where appropriate.
- [x] 2.4 Migrate remaining model families in dependency order.
- [x] 2.5 Remove superseded property and string-metadata boilerplate.

## 3. Verification

- [x] 3.1 Run round-trip tests against representative fixtures.
- [x] 3.2 Verify public constructors, representations, and serialization behavior.
- [x] 3.3 Publish migration documentation for changed constructors and types.
