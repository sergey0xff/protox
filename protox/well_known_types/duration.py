import typing

import protox


class Duration(protox.Message):
    seconds: typing.Optional[int]
    nanos: typing.Optional[int]

    def __init__(
        self,
        *,
        seconds: typing.Optional[int] = None,
        nanos: typing.Optional[int] = None,
    ):
        super().__init__(
            seconds=seconds,
            nanos=nanos,
        )


protox.define_fields(
    Duration,
    seconds=protox.Int64(
        number=1, required=False
    ),
    nanos=protox.Int32(
        number=2, required=False
    ),
)
