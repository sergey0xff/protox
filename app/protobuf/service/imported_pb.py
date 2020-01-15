import typing
from enum import IntEnum

import protox


class ImportedMessage(protox.Message):
    class Hello(IntEnum):
        ONE = 0
        TWO = 1
        THREE = 2

    class Nested(protox.Message):
        x: typing.Optional[int]

        def __init__(
            self,
            *,
            x: typing.Optional[int] = None,
        ):
            super().__init__(
                x=x,
            )

    x: typing.Optional[int]

    def __init__(
        self,
        *,
        x: typing.Optional[int] = None,
    ):
        super().__init__(
            x=x,
        )


protox.define_fields(
    ImportedMessage,
    x=protox.Int32(
        number=1, required=False
    ),
)

protox.define_fields(
    ImportedMessage.Nested,
    x=protox.Int32(
        number=1, required=False
    ),
)
