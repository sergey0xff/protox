from protox import Message, fields


class DoubleValue(Message):
    value: float = fields.Double(number=1)


class FloatValue(Message):
    value: float = fields.Float(number=1)


class Int64Value(Message):
    value: int = fields.Int64(number=1)


class UInt64Value(Message):
    value: int = fields.UInt64(number=1)


class Int32Value(Message):
    value: int = fields.Int32(number=1)


class UInt32Value(Message):
    value: int = fields.UInt32(number=1)


class BoolValue(Message):
    value: bool = fields.Bool(number=1)


class StringValue(Message):
    value: str = fields.String(number=1)


class BytesValue(Message):
    value: bytes = fields.Bytes(number=1)
