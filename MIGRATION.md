# Migrating to 2.0

`EcobeeService` remains the supported client entry point, and the roughly forty API
operations on it keep the names and signatures they had in 1.3.13. What changed is
credentials: how you hand them over, how they are stored, and when they are renewed.
Start with the credentials section, because a 1.x application will not construct a
service until that work is done.

## Credentials

The constructor now takes four arguments, all required:

```python
EcobeeService(thermostat_name, application_key, tokens, on_tokens_changed)
```

`tokens` is the credentials you already hold, as a `Tokens` or a mapping.
`on_tokens_changed` is called with a new `Tokens` every time ecobee issues credentials.
ecobee replaces the refresh token each time it issues one, so an application that
discards what the callback hands it will lose access. If the callback raises, the
exception reaches the caller and the new credentials remain available through
`service.tokens` while the process is still running.

> [!WARNING]
> Catch storage callback exceptions and recover `service.tokens` before the process
> exits. ecobee has already invalidated the previous refresh token when the callback
> runs. If the process exits before the new credentials are stored, they are lost and
> the application must authorize again.

These are gone:

| Removed in 2.0                                                                                                                                       | Replacement                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| The `authorization_token`, `access_token`, `refresh_token`, `access_token_expires_on`, `refresh_token_expires_on` and `scope` keyword arguments.     | Pass a `Tokens` as the third argument.                                                                 |
| The setters for those properties.                                                                                                                    | `Tokens` is immutable. The service replaces the whole value and announces it.                          |
| `EcobeeService.from_tokens()`.                                                                                                                       | The one constructor.                                                                                   |
| `EcobeeService.attribute_name_map` and `attribute_type_map`, and the same two attributes on `EcobeeApiException` and `EcobeeAuthorizationException`. | Nothing reads them. Credentials serialize through `Tokens.to_dict()`.                                  |
| `Utilities.make_http_request()` and `pyecobee.utilities.transport`.                                                                                  | The operations on `EcobeeService`, which sign and send requests for you.                               |
| `Utilities.dictionary_to_object()` and `Utilities.object_to_dictionary()`.                                                                           | Responses arrive as models already. Serialize one with `to_api_dict()`.                                |
| `Utilities.process_http_response()`.                                                                                                                 | Import `process_http_response()` from `pyecobee.utilities` if you process raw HTTP responses yourself. |

Renewal is automatic. Before each request the service renews an access token that is
within two minutes of expiring, and if ecobee reports a token as already expired it
renews once and retries. You can delete the pro-active and reactive patterns the 1.x
README taught, which compared expiries before every call and caught status code 14.

`JsonFileTokenStore` is a ready-made pair of callables for the third and fourth
arguments:

```python
from pyecobee import EcobeeService, JsonFileTokenStore

store = JsonFileTokenStore("~/.config/pyecobee/tokens.json")
service = EcobeeService("My Thermostat", application_key, store.load(), store.save)
```

## Moving credentials out of a shelf

A shelf written by 1.x cannot be read by 2.0. The 1.x README taught pickling the whole
service into `shelve`, and unpickling one under 2.0 raises:

```text
AttributeError: 'EcobeeService' object has no attribute '_thermostat_name' and no __dict__ for setting new attributes
```

That state moved into an internal component, so the pickle no longer describes the
class. Extract the credentials once, with 1.3.13 still installed, under the interpreter
that wrote the shelf:

```python
import json
import shelve

with shelve.open("pyecobee_db") as database:
    service = database["My Thermostat"]

with open("tokens.json", "w") as file:
    json.dump(
        {
            "access_token": service.access_token,
            "refresh_token": service.refresh_token,
            "access_token_expires_on": service.access_token_expires_on.isoformat(),
            "refresh_token_expires_on": service.refresh_token_expires_on.isoformat(),
            "scope": service.scope.value,
        },
        file,
        indent=2,
    )
```

The file holds credentials, so restrict it with `chmod 600 tokens.json`. Its contents
match the mapping accepted by `Tokens.from_dict()`:

```python
import json

from pyecobee import EcobeeService, Tokens

with open("tokens.json") as file:
    tokens = Tokens.from_dict(json.load(file))

service = EcobeeService(
    "My Thermostat",
    application_key,
    tokens,
    save_tokens,
)
```

Alternatively, let `JsonFileTokenStore` load the file and save future credentials:

```python
from pyecobee import EcobeeService, JsonFileTokenStore

store = JsonFileTokenStore("tokens.json")
service = EcobeeService("My Thermostat", application_key, store.load(), store.save)
```

Once the 2.0 service loads successfully, delete the shelf. 1.x recorded refresh tokens
as lasting a year. 2.0 records 30 days, which is what ecobee documents, and applies
that the next time credentials are issued.

## Public imports

Use explicit package-root imports for application code:

```python
from pyecobee import EcobeeService, Selection, SelectionType, Thermostat
```

The `pyecobee.objects.*` compatibility modules are gone; import models from the
package root or `pyecobee.models` instead.

The package root now defines `__all__`. Names that were incidentally exposed
through wildcard imports, such as the standard-library `logging` module, are no
longer public API. Import those directly from their owning module.

The domain components under `pyecobee.services` are implementation details. Keep
using `EcobeeService` unless a later release makes one of them public.

## Object models

Object and response classes are now Pydantic v2 models. Most public Python field
names are unchanged, while their ecobee names are declared as Pydantic aliases in
`pyecobee.models`. Constructor arguments that formerly escaped a name with a trailing
underscore now use the unescaped field name.

| Previous behavior                                                                                                               | Version 2 behavior                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Constructors accepted arbitrary keyword arguments or unchecked values.                                                          | Model constructors reject unknown fields and invalid enum values with `pydantic.ValidationError`.                        |
| `Utilities.object_to_dictionary()` reflected `__slots__` and string field metadata.                                             | Call the model's `to_api_dict()` method.                                                                                 |
| Constructor arguments such as `Function(type_=...)` and `RemoteSensor(id_=...)` escaped field names with a trailing underscore. | Use the field name directly, such as `Function(type="resumeProgram")` and `RemoteSensor(id="sensor-id", type="sensor")`. |
| Response conversion manually traversed string type metadata.                                                                    | Response conversion uses typed Pydantic validation; unknown API fields are ignored for forward compatibility.            |
| Models exposed private slot-backed storage.                                                                                     | Fields are public Pydantic attributes; use `model_dump()` or `to_api_dict()` rather than private attributes.             |

Pass documented Python names or ecobee aliases when constructing a model. For
example:

```python
selection = Selection(selection_type=SelectionType.THERMOSTATS, selection_match="123")
payload = selection.to_api_dict()
```

Model construction is strict. Responses deserialized by the service stay tolerant of
fields ecobee adds after this release. Existing response fields keep their Python names,
and enum-valued fields serialize as their ecobee string values.
