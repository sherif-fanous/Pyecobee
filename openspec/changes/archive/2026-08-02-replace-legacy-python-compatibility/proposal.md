## Why

After Python 3.12 becomes the minimum, six, enum34, pytz, and Python 2 compatibility branches add unnecessary complexity and obscure the actual type and time behavior of the library.

## What Changes

- **BREAKING**: Remove six-based string and exception compatibility APIs.
- Remove enum34 compatibility and use the standard enum module exclusively.
- Replace pytz usage with datetime.UTC and zoneinfo.
- Replace Python 2 syntax, compatibility comments, and old classifiers.
- Make timezone-aware datetime requirements explicit for report operations.

## Capabilities

### New Capabilities
- `native-python-runtime`: Defines native Python 3.12 string, enum, exception, and timezone behavior.

### Modified Capabilities

## Impact

Affects service validation, utility deserialization metadata, exception handling, tests, documentation, and runtime dependencies. Existing consumers using legacy compatibility types or relying on pytz-specific objects may need migration.
