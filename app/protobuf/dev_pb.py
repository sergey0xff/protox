import typing

import protox


class Debug(protox.Message):
    class Nested(protox.Message):
        class Three(protox.Message):
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
    Debug.Nested.Three,
    x=protox.Int32(
        number=1, required=False
    ),
)
