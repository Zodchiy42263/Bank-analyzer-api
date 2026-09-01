from typing import Any

from flask import abort
from pydantic import ValidationError, BaseModel


def validate_data(schema: type[BaseModel], data: Any):
    try:
        validated_data = schema.model_validate(data)
        return validated_data
    except ValidationError:
        abort(400, "Некорректные входные данные.")
