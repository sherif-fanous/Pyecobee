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
