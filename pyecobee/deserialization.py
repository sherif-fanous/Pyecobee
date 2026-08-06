"""Safe conversion of ecobee API payloads into Pydantic response models."""

from __future__ import annotations

import logging
from typing import Any, get_args, get_origin

from pydantic import ValidationError

from pyecobee import models
from pyecobee.ecobee_object import EcobeeObject
from pyecobee.exceptions import EcobeeDeserializationException

logger = logging.getLogger(__name__)


MODEL_REGISTRY = {
    name: value
    for name, value in vars(models).items()
    if isinstance(value, type) and issubclass(value, EcobeeObject)
}


def _nested_model(annotation: Any) -> type[EcobeeObject] | None:
    """Find a Pydantic model in a field annotation."""

    if isinstance(annotation, type) and issubclass(annotation, EcobeeObject):
        return annotation

    for argument in get_args(annotation):
        model = _nested_model(argument)

        if model is not None:
            return model

    return None


def _known_fields(data: Any, model: type[EcobeeObject]) -> Any:
    """Discard forward-compatible response fields before strict nested validation."""

    if not isinstance(data, dict):
        return data

    known: dict[str, Any] = {}

    recognized_names = {
        candidate
        for name, field in model.model_fields.items()
        for candidate in (name, field.alias or name)
    }

    for key in data.keys() - recognized_names:
        logger.warning("Ignoring unknown field %s on %s", key, model.__name__)

    for name, field in model.model_fields.items():
        alias = field.alias or name

        if alias not in data and name not in data:
            continue

        key = alias if alias in data else name
        value = data[key]

        nested = _nested_model(field.annotation)
        origin = get_origin(field.annotation)

        if nested is not None:
            if origin is list and isinstance(value, list):
                value = [_known_fields(item, nested) for item in value]
            elif isinstance(value, dict):
                value = _known_fields(value, nested)

        known[key] = value

    return known


def deserialize[EcobeeObjectT: EcobeeObject](
    data: dict[str, Any], model: type[EcobeeObjectT], path: str | None = None
) -> EcobeeObjectT:
    """Construct *model* from an API object without evaluating source text."""

    path = path or model.__name__

    if not isinstance(data, dict):
        raise EcobeeDeserializationException(f"{path} must be an object")

    try:
        return model.model_validate(_known_fields(data, model))
    except ValidationError as error:
        raise EcobeeDeserializationException(f"Invalid {path}: {error}") from error
