import typing
from enum import IntEnum

import protox


class Debug(protox.Message):
    class Nested(protox.Message):
        class Number(IntEnum):
            A = 0

        number: typing.Optional['Debug.Nested.Number']

        def __init__(
            self,
            *,
            number: typing.Optional['Debug.Nested.Number'] = None,
        ):
            super().__init__(
                number=number,
            )

    nested: typing.Optional['Debug.Nested']
    nested_map: typing.Dict[int, 'Debug.Nested.Number']

    def __init__(
        self,
        *,
        nested: typing.Optional['Debug.Nested'] = None,
        nested_map: typing.Dict[int, 'Debug.Nested.Number'] = None,
    ):
        super().__init__(
            nested=nested,
            nested_map=nested_map,
        )


protox.define_fields(
    Debug.Nested,
    number=protox.EnumField(
        number=1, py_enum=Debug.Nested.Number, required=False
    ),
)

protox.define_fields(
    Debug,
    nested=Debug.Nested.as_field(
        number=1, required=False
    ),
    nested_map=protox.MapField(
        number=2, key=protox.Int32, value=Debug.Nested.Number
    ),
)
