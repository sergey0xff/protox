from enum import IntEnum
from typing import List, Dict, Optional, Union

from protox import Message, fields, one_of, MapField
from protox.message import define_fields


class NullValue(IntEnum):
    NULL_VALUE = 0


class Struct(Message):
    fields: Dict[str, 'Value']  # figure out the best interface for value

    def __setitem__(
        self,
        key: str,
        value: Union[type(None), float, str, bool, 'Struct', list]
    ):
        self.fields[key] = value

    def __getitem__(self, item: str):
        return self.fields[item]


class Value(Message):
    null_value: Optional[NullValue] = fields.EnumField(NullValue, number=1, required=False)
    number_value: Optional[float] = fields.Double(number=2, required=False)
    string_value: Optional[str] = fields.String(number=3, required=False)
    bool_value: Optional[bool] = fields.Bool(number=4, required=False)
    struct_value: Optional[Struct] = Struct.as_field(number=5, required=False)
    list_value: Optional['ListValue']

    kind = one_of(
        'null_value',
        'number_value',
        'string_value',
        'bool_value',
        'struct_value',
        'list_value',
    )


class ListValue(Message):
    values: List = Value.as_repeated(number=1)


# Struct delayed fields
define_fields(
    Struct,
    fields=MapField(
        fields.String,
        Value.as_field,
        number=1
    )
)

# Value delayed fields
define_fields(
    Value,
    null_value=fields.EnumField(NullValue, number=1, required=False),
    list_value=ListValue.as_field(number=6, required=False),
)

struct = Struct()
struct['key'] = Value()
