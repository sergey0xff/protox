import json
from enum import IntEnum
from typing import Dict, List, Iterable, Union, MutableMapping, Iterator

from protox import Message, fields, one_of, define_fields

PyValue_T = Union[
    type(None),
    float,
    int,
    str,
    bool,
    dict,
    Iterable,
]


class Struct(
    Message,
    MutableMapping
):
    _fields: Dict[str, 'Value']

    def __init__(self, initial_value: Dict[str, PyValue_T] = None, **kwargs):
        super().__init__()

        if isinstance(initial_value, Dict):
            for key, value in initial_value.items():
                self[key] = value

        for key, value in kwargs.items():
            self[key] = value

    def __str__(self):
        return f'Struct {json.dumps(self.to_python(), indent=2, ensure_ascii=False)}'

    def __setitem__(self, key: str, value: PyValue_T):
        self._fields[key] = Value.from_python(value)

    def __getitem__(self, key: str) -> PyValue_T:
        return Value.to_python(self._fields[key])

    def __delitem__(self, key: str) -> None:
        del self._fields[key]

    def __len__(self) -> int:
        return len(self._fields)

    def __iter__(self) -> Iterator[PyValue_T]:
        return iter(self._fields)

    def to_python(self) -> PyValue_T:
        return {
            key: value.to_python()
            for key, value in self._fields.items()
        }

    @classmethod
    def from_python(cls, value: dict) -> 'Struct':
        return Struct(value)


class NullValue(IntEnum):
    NULL_VALUE = 0


class Value(Message):
    null_value: NullValue = fields.EnumField(NullValue, number=1)
    number_value: float = fields.Double(number=2)
    string_value: str = fields.String(number=3)
    bool_value: bool = fields.Bool(number=4)
    struct_value: Struct = Struct.as_field(number=5)
    list_value: 'ListValue'

    kind = one_of(
        'null_value',
        'number_value',
        'string_value',
        'bool_value',
        'struct_value',
        'list_value',
    )

    @classmethod
    def from_python(cls, value) -> 'Value':
        if value is None:
            return Value(
                null_value=NullValue.NULL_VALUE
            )
        elif isinstance(value, (int, float)):
            return Value(
                number_value=value
            )
        elif isinstance(value, str):
            return Value(
                string_value=value
            )
        elif isinstance(value, bool):
            return Value(
                bool_value=value
            )
        elif isinstance(value, dict):
            return Value(
                struct_value=Struct(**value)
            )
        elif isinstance(value, Struct):
            return Value(
                struct_value=value
            )
        elif isinstance(value, Iterable):
            return Value(
                list_value=ListValue.from_python(value)
            )

        raise ValueError(
            f'Invalid value {value!r}'
        )

    def to_python(self) -> PyValue_T:
        kind = self.which_one_of('kind')

        if kind is None:
            return None

        py_value = getattr(self, kind)

        if py_value == NullValue.NULL_VALUE:
            return None
        elif isinstance(py_value, (Struct, ListValue)):
            return py_value.to_python()
        elif isinstance(py_value, float):
            if py_value.is_integer():
                return int(py_value)

        return py_value


class ListValue(Message):
    values: List[Value] = Value.as_repeated(number=1)

    @classmethod
    def from_python(cls, value: Iterable) -> 'ListValue':
        return cls(
            values=[Value.from_python(x) for x in value]
        )

    def to_python(self) -> List[PyValue_T]:
        return [x.to_python() for x in self.values]


define_fields(
    Struct,
    _fields=fields.MapField(
        key=fields.String,
        value=Value,
        number=1,
    )
)

define_fields(
    Value,
    list_value=ListValue.as_field(number=6)
)
