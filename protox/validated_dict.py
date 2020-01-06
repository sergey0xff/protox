from typing import Optional, Dict

from protox.fields import MapField


class ValidatedDict(Dict):
    def __init__(
        self,
        map_field: MapField,
        initial_value: Optional[dict] = None
    ):
        super().__init__()

        self._map_field = map_field
        self._validate_key = map_field.key_field.validate_value
        self._validate_value = map_field.value_field.validate_value

        for key, value in (initial_value or {}).items():
            self[key] = value

    def copy(self):
        return ValidatedDict(
            self._map_field,
            super().copy()
        )

    def __setitem__(self, key, value):
        self._validate_key(key)
        self._validate_value(value)

        return super().__setitem__(key, value)
