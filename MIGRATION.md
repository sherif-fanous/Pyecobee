# Migrating to 2.0

`EcobeeService` remains the supported client entry point. Its existing methods and
method signatures are unchanged; internally, operations are now delegated to
domain-specific service components.

## Public imports

Use explicit imports for application code:

```python
from pyecobee import EcobeeService, Selection, SelectionType
from pyecobee.objects.thermostat import Thermostat
```

The package root now defines `__all__`. Names that were incidentally exposed
through wildcard imports, such as the standard-library `logging` module, are no
longer public API. Import those directly from their owning module.

The domain components under `pyecobee.services` are implementation details;
applications should continue to use `EcobeeService` unless a future release
makes a domain component public.

## Object models

Object and response classes are now Pydantic v2 models.  Their public Python
field names are unchanged, while their ecobee names are declared as Pydantic
aliases in `pyecobee.models`.

| Previous behavior | Version 2 behavior |
| --- | --- |
| Constructors accepted arbitrary keyword arguments or unchecked values. | Request-model constructors reject unknown fields and invalid enum values with `pydantic.ValidationError`. |
| `Utilities.object_to_dictionary()` reflected `__slots__` and string field metadata. | It serializes models with `model_dump(by_alias=True, exclude_none=True, mode="json")`. |
| Response conversion manually traversed string type metadata. | Response conversion uses typed Pydantic validation; unknown API fields are ignored for forward compatibility. |
| Models exposed private slot-backed storage. | Fields are public Pydantic attributes; use `model_dump()` or `to_api_dict()` rather than private attributes. |

Pass documented Python names or ecobee aliases when constructing a model. For
example:

```python
selection = Selection(selection_type=SelectionType.THERMOSTATS, selection_match="123")
payload = selection.model_dump(by_alias=True, exclude_none=True, mode="json")
```

`Selection` is a strict request model. API responses remain tolerant of fields
introduced by ecobee after this release. Existing response fields retain their
Python names and enum-valued fields serialize as their ecobee string values.
