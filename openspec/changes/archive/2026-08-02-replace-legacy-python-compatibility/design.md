## Context

The code stores string type names such as `six.text_type`, checks `six.string_types`, uses six.reraise, and localizes datetimes with pytz. Python 3.12 provides the required native functionality.

## Goals / Non-Goals

**Goals:**
- Remove compatibility dependencies and branches.
- Preserve public validation and exception semantics where possible.
- Make aware datetime behavior explicit and testable.

**Non-Goals:**
- Replace the serializer's string metadata in full; that belongs to the deserializer change.
- Change API date formats.
- Redesign all model classes.

## Decisions

Use `str`, native `enum`, `datetime.UTC`, and `zoneinfo.ZoneInfo`. Use exception chaining with `raise ... from exc` instead of six.reraise. Reject naive datetimes explicitly rather than silently assigning a timezone.

## Risks / Trade-offs

- [Risk] Consumers pass pytz-localized datetime instances. → Aware datetime instances remain accepted by the datetime protocol; document zoneinfo examples and test normalization.
- [Risk] Removing string metadata names breaks temporary validation code. → Update metadata references in the same change and cover them with baseline tests.
