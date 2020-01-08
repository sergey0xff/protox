from typing import Optional

from protox import Message, fields


class DoubleValue(Message):
    value: Optional[float] = fields.Double(number=1)


class FloatValue(Message):
    value: Optional[float] = fields.Float(number=1)


class Int64Value(Message):
    value: Optional[int] = fields.Int64(number=1)


class UInt64Value(Message):
    value: Optional[int] = fields.UInt64(number=1)


class Int32Value(Message):
    value: Optional[int] = fields.Int32(number=1)


class UInt32Value(Message):
    value: Optional[int] = fields.UInt32(number=1)


class BoolValue(Message):
    value: Optional[bool] = fields.Bool(number=1)


class StringValue(Message):
    value: Optional[str] = fields.String(number=1)


class BytesValue(Message):
    value: Optional[bytes] = fields.Bytes(number=1)
