import typing

import protox


class Any(protox.Message):
    type_url: typing.Optional[str]
    value: typing.Optional[bytes]

    def __init__(
        self,
        *,
        type_url: typing.Optional[str] = None,
        value: typing.Optional[bytes] = None,
    ):
        super().__init__(
            type_url=type_url,
            value=value,
        )


protox.define_fields(
    Any,
    type_url=protox.String(
        number=1, required=False
    ),
    value=protox.Bytes(
        number=2, required=False
    ),
)
