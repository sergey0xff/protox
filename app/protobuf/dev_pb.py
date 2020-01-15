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
