from typing import Iterable, List


class ValidatedList(List):
    def __init__(self, field, iterable=tuple()):
        self._field = field
        super().__init__(iterable)

    def append(self, x):
        self._field.validate_value(x)
        super().append(x)

    def extend(self, iterable: Iterable):
        validated_iterable = []

        for item in iterable:
            self._field.validate_value(item)
            validated_iterable.append(item)

        super().extend(validated_iterable)

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            for x in value:
                self._field.validate_value(x)
        else:
            self._field.validate_value(value)

        super().__setitem__(index, value)
