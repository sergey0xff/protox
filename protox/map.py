class MapGetter:
    pass


class MapSetter:
    pass


class ValidateMap(dict):
    def __init__(self, key_field, value_field, iterable=tuple()):
        super().__init__(iter)
        self._key_field = key_field
        self._value_field = value_field

    def __getitem__(self, item):
        super().__getitem__(item)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
