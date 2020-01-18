import typing

import protox


class DoubleValue(protox.Message):
    value: typing.Optional[float]

    def __init__(
        self,
        *,
        value: typing.Optional[float] = None,
    ):
        super().__init__(
            value=value,
        )


class FloatValue(protox.Message):
    value: typing.Optional[float]

    def __init__(
        self,
        *,
        value: typing.Optional[float] = None,
    ):
        super().__init__(
            value=value,
        )


class Int64Value(protox.Message):
    value: typing.Optional[int]

    def __init__(
        self,
        *,
        value: typing.Optional[int] = None,
    ):
        super().__init__(
            value=value,
        )


class UInt64Value(protox.Message):
    value: typing.Optional[int]

    def __init__(
        self,
        *,
        value: typing.Optional[int] = None,
    ):
        super().__init__(
            value=value,
        )


class Int32Value(protox.Message):
    value: typing.Optional[int]

    def __init__(
        self,
        *,
        value: typing.Optional[int] = None,
    ):
        super().__init__(
            value=value,
        )


class UInt32Value(protox.Message):
    value: typing.Optional[int]

    def __init__(
        self,
        *,
        value: typing.Optional[int] = None,
    ):
        super().__init__(
            value=value,
        )


class BoolValue(protox.Message):
    value: typing.Optional[bool]

    def __init__(
        self,
        *,
        value: typing.Optional[bool] = None,
    ):
        super().__init__(
            value=value,
        )


class StringValue(protox.Message):
    value: typing.Optional[str]

    def __init__(
        self,
        *,
        value: typing.Optional[str] = None,
    ):
        super().__init__(
            value=value,
        )


class BytesValue(protox.Message):
    value: typing.Optional[bytes]

    def __init__(
        self,
        *,
        value: typing.Optional[bytes] = None,
    ):
        super().__init__(
            value=value,
        )


protox.define_fields(
    DoubleValue,
    value=protox.Double(
        number=1, required=False
    ),
)

protox.define_fields(
    FloatValue,
    value=protox.Float(
        number=1, required=False
    ),
)

protox.define_fields(
    Int64Value,
    value=protox.Int64(
        number=1, required=False
    ),
)

protox.define_fields(
    UInt64Value,
    value=protox.UInt64(
        number=1, required=False
    ),
)

protox.define_fields(
    Int32Value,
    value=protox.Int32(
        number=1, required=False
    ),
)

protox.define_fields(
    UInt32Value,
    value=protox.UInt32(
        number=1, required=False
    ),
)

protox.define_fields(
    BoolValue,
    value=protox.Bool(
        number=1, required=False
    ),
)

protox.define_fields(
    StringValue,
    value=protox.String(
        number=1, required=False
    ),
)

protox.define_fields(
    BytesValue,
    value=protox.Bytes(
        number=1, required=False
    ),
)
