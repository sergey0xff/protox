import enum
import io
import struct
from abc import ABC, abstractmethod
from typing import IO, Type, Optional, List, Dict, Tuple, Iterable, BinaryIO, Union

from protox.constants import (
    MIN_INT32, MAX_INT32, MIN_INT64, MAX_INT64, MIN_UINT32,
    MAX_UINT32, MAX_UINT64, MIN_UINT64, MAX_FLOAT, MAX_DOUBLE
)
from protox.encoding import (
    decode_bytes, encode_varint, decode_varint, encode_zig_zag32,
    decode_zig_zag, encode_zig_zag64, encode_bytes
)
from protox.exceptions import MessageDecodeError, FieldValidationError

__all__ = [
    'WireType',
    'Field',
    'Int32',
    'Int64',
    'SInt32',
    'SInt64',
    'UInt32',
    'UInt64',
    'Bytes',
    'String',
    'Bool',
    'EnumField',
    'Fixed32',
    'Fixed64',
    'SFixed32',
    'SFixed64',
    'Float',
    'Double',
    'MessageField',
    'Repeated',
    'OneOf',
    'one_of',
    'MapField',
]


class WireType(enum.IntEnum):
    VARINT = 0
    FIXED_64 = 1
    LENGTH = 2
    START_GROUP = 3  # Will not be implemented. Deprecated by protobuf
    END_GROUP = 4  # Will not be implemented. Deprecated by protobuf
    FIXED_32 = 5


class Field(ABC):
    wire_type: WireType  # should be provided by subclasses

    def __init__(self, *, number: int, default=None, required: bool = False):
        self._validate_field_number(number)

        self._number = number
        self._required = required
        self._header = encode_varint(self.number << 3 | self.wire_type)
        self._default = default

        # the name of the field is set by message because it's known in the message
        self.name: Optional[str] = None

    @property
    def number(self):
        return self._number

    @property
    def default(self):
        return self._default

    @property
    def required(self):
        return self._required

    @abstractmethod
    def encode_value(self, value) -> bytes:
        raise NotImplementedError()

    def encode(self, value) -> bytes:
        """
        Encode value with header
        """
        return self.header + self.encode_value(value)

    @abstractmethod
    def decode(self, stream: IO):
        raise NotImplementedError()

    @abstractmethod
    def validate_value(self, value):
        raise NotImplementedError()

    @property
    def header(self) -> bytes:
        return self._header

    @classmethod
    def as_repeated(cls, *, number: int, packed: bool = False) -> 'Repeated':
        return Repeated(
            of_type=cls,
            number=number,
            packed=packed,
        )

    @staticmethod
    def _validate_field_number(number):
        if number not in range(1, 2 ** 29) or number in range(19_000, 20_000):
            raise FieldValidationError(
                'Field number {} is invalid. '
                'A valid field number should be in range [1..2 ** 29 -1] '
                'excluding range [19_000..19_999] '
                'which is reserved for the protobuf implementation'
            )


class BaseRepeatedStrategy(ABC):
    def __init__(self, field: Field, number: int):
        self._field = field
        self._number = number

    @abstractmethod
    def encode(self, values: list) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def decode(self, stream: IO):
        raise NotImplementedError()


class PackedRepeatedStrategy(BaseRepeatedStrategy):
    wire_type = WireType.LENGTH

    def encode(self, values: list) -> bytes:
        if not values:
            return b''

        data = bytearray()

        for item in values:
            data += self._field.encode_value(item)

        return (
            encode_varint(self._field.number << 3 | WireType.LENGTH) +
            encode_bytes(data)
        )

    def decode(self, stream: IO) -> list:
        length = decode_varint(stream)

        items = []

        data = stream.read(length)

        if len(data) < length:
            raise MessageDecodeError(
                f'Expected to read {length:_} bytes, read {len(data):_} bytes instead'
            )

        stream = io.BytesIO(data)

        while stream.seek(0, io.SEEK_CUR) < length:
            items.append(self._field.decode(stream))

        return items


class UnpackedRepeatedStrategy(BaseRepeatedStrategy):
    @property
    def wire_type(self):
        return self._field.wire_type

    def encode(self, values: list) -> bytes:
        if not values:
            return b''

        data = bytearray()

        for item in values:
            data += self._field.header + self._field.encode_value(item)

        return data

    def decode(self, stream: IO):
        """
        From docs:
        "repeated values do not have to appear consecutively;
        they may be interleaved with other fields."

        That's why we can only read exactly one item at a time
        """
        return self._field.decode(stream)


class Repeated(Field):
    def __init__(self, of_type: Type, *, number: int, packed: bool = False):
        from .message import Message

        if issubclass(of_type, Message):
            if packed:
                raise FieldValidationError(
                    f'Field of type {of_type.__name__!r}. Packed repeated fields only support primitive types'
                )
            self._field = MessageField(of_type, number=number)
        elif issubclass(of_type, enum.IntEnum):
            self._field = EnumField(of_type, number=number)
        else:
            self._field = of_type(number=number)

        self._of_type = of_type
        self._packed = packed
        self._strategy: BaseRepeatedStrategy

        if packed:
            self._strategy = PackedRepeatedStrategy(self._field, number)
        else:
            self._strategy = UnpackedRepeatedStrategy(self._field, number)

        self.wire_type = self._strategy.wire_type

        super().__init__(number=number)

    @classmethod
    def as_repeated(cls, *, number: int, packed: bool = False) -> 'Repeated':
        raise Exception(
            'Cannot created repeated from repeated'
        )

    @property
    def field(self):
        return self._field

    @property
    def of_type(self):
        return self._of_type

    @property
    def packed(self):
        return self._packed

    def encode(self, values: list) -> bytes:
        return self._strategy.encode(values)

    def encode_value(self, values: list) -> bytes:
        return self._strategy.encode(values)

    def decode(self, stream: IO) -> list:
        return self._strategy.decode(stream)

    def validate_value(self, values: Iterable):
        if not isinstance(values, Iterable):
            raise ValueError(
                f'Repeated field {self.name!r} should be a \'list\' or \'tuple\', got {type(values).__name__!r} instead'
            )

        for value in values:
            self._field.validate_value(value)


class Int(Field):
    min_value: int
    max_value: int
    wire_type = WireType.VARINT

    def encode_value(self, value: int) -> bytes:
        if value < 0:
            value += 2 ** 64

        return encode_varint(value)

    def decode(self, stream: IO) -> int:
        value = decode_varint(stream)

        if value > 2 ** 63 - 1:
            value -= 2 ** 64

        return value

    def validate_value(self, value: int):
        if not isinstance(value, int):
            raise ValueError(
                f"Expected a value of type 'int', "
                f"got {type(value).__name__!r} instead"
            )

        if value < self.min_value:
            raise ValueError(
                f'Value {value!r} is less than min value {self.min_value!r} '
                f'of type {type(self).__name__}'
            )

        if value > self.max_value:
            raise ValueError(
                f'Value {value} is greater than max value {self.max_value} '
                f'of type {type(self).__name__}'
            )


class UInt(Int, ABC):
    def decode(self, stream: IO) -> int:
        return decode_varint(stream)


class SInt(Int, ABC):
    def decode(self, stream: IO) -> int:
        zig_zag_value = decode_varint(stream)
        return decode_zig_zag(zig_zag_value)


class Int32(Int):
    min_value: int = MIN_INT32
    max_value: int = MAX_INT32


class Int64(Int):
    min_value: int = MIN_INT64
    max_value: int = MAX_INT64


class UInt32(UInt):
    min_value: int = MIN_UINT32
    max_value: int = MAX_UINT32


class UInt64(UInt):
    min_value: int = MIN_UINT64
    max_value: int = MAX_UINT64


class SInt32(SInt):
    min_value: int = MIN_INT32
    max_value: int = MAX_INT32

    def encode_value(self, value: int) -> bytes:
        zig_zag_value = encode_zig_zag32(value)
        return encode_varint(zig_zag_value)


class SInt64(SInt):
    min_value: int = MIN_INT64
    max_value: int = MAX_INT64

    def encode_value(self, value: int) -> bytes:
        zig_zag_value = encode_zig_zag64(value)
        return encode_varint(zig_zag_value)


class Bytes(Field):
    wire_type = WireType.LENGTH

    def encode_value(self, value: bytes) -> bytes:
        return encode_bytes(value)

    def decode(self, stream: IO) -> bytes:
        return decode_bytes(stream)

    def validate_value(self, value: bytes):
        if not isinstance(value, bytes):
            raise ValueError(
                f"Expected a value of type 'bytes', "
                f"got {type(value).__name__!r} instead"
            )


class String(Field):
    wire_type = WireType.LENGTH

    def encode_value(self, value: str) -> bytes:
        data = value.encode('utf-8')
        return encode_bytes(data)

    def decode(self, stream: IO) -> str:
        data = decode_bytes(stream)
        return data.decode('utf-8')

    def validate_value(self, value: str):
        if not isinstance(value, str):
            raise ValueError(
                f"Expected a value of type 'str', "
                f"got {type(value).__name__!r} instead"
            )


class Bool(Field):
    wire_type = WireType.VARINT

    def encode_value(self, value: bool) -> bytes:
        return chr(value).encode()

    def decode(self, stream: IO) -> bool:
        value = decode_varint(stream)
        return bool(value)

    def validate_value(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(
                f"Expected a value of type 'bool', "
                f"got {type(value).__name__!r} instead"
            )


class EnumField(Field):
    wire_type = WireType.VARINT

    def __init__(
        self,
        py_enum: Type[enum.IntEnum],
        *,
        number,
        default=None,
        required=False,
    ):
        self._validate_py_enum(py_enum)

        super().__init__(
            number=number,
            default=default,
            required=required,
        )

        self._py_enum = py_enum

    def encode_value(self, value: int) -> bytes:
        return encode_varint(value)

    def decode(self, stream: IO) -> Optional[int]:
        value = decode_varint(stream)

        # Specifications: omit value that's not in the enum's variants
        if value in list(self._py_enum):
            return self._py_enum(value)

        return None

    def validate_value(self, value: int):
        valid_values = [int(x) for x in self._py_enum]

        if value not in valid_values:
            raise ValueError(
                f'Expected an enum value of {repr(valid_values)}, got {value} instead'
            )

    @staticmethod
    def _validate_py_enum(py_enum: Type[enum.IntEnum]):
        if not issubclass(py_enum, enum.IntEnum):
            raise FieldValidationError(
                f'Enum field should be a subclass of IntEnum, got {py_enum!r} instead'
            )

        for variant in py_enum:
            if not -2 ** 31 <= variant.value <= 2 ** 31 - 1:
                raise FieldValidationError(
                    f'Invalid enum field variant {variant.value}. Should be in range [-2 ** 31 .. 2 ** 31 - 1]'
                )


class Fixed32(Int):
    min_value = MIN_UINT32
    max_value = MAX_UINT32
    wire_type = WireType.FIXED_32

    def encode_value(self, value: int) -> bytes:
        return struct.pack('<I', value)

    def decode(self, stream: IO) -> int:
        data = stream.read(4)

        if len(data) != 4:
            raise MessageDecodeError(
                f"Expected to read 4 bytes, got {len(data)} bytes instead"
            )

        return struct.unpack('<I', data)[0]


class Fixed64(Int):
    min_value = MIN_UINT64
    max_value = MAX_UINT64
    wire_type = WireType.FIXED_64

    def encode_value(self, value: int) -> bytes:
        return struct.pack('<Q', value)

    def decode(self, stream: IO) -> int:
        data = stream.read(8)

        if len(data) != 8:
            raise MessageDecodeError(
                f"Expected to read 8 bytes, got {len(data)} bytes instead"
            )

        return struct.unpack('<Q', data)[0]


class SFixed32(Int):
    min_value = MIN_INT32
    max_value = MAX_INT32
    wire_type = WireType.FIXED_32

    def encode_value(self, value: int) -> bytes:
        return struct.pack('<i', value)

    def decode(self, stream: IO) -> int:
        data = stream.read(4)

        if len(data) < 4:
            raise MessageDecodeError(
                f"Expected to read 4 bytes, got {len(data)} bytes instead"
            )

        return struct.unpack('<i', data)[0]


class SFixed64(Int):
    min_value = MIN_INT64
    max_value = MAX_INT64
    wire_type = WireType.FIXED_64

    def encode_value(self, value: int) -> bytes:
        return struct.pack('<q', value)

    def decode(self, stream: IO) -> int:
        data = stream.read(8)

        if len(data) < 8:
            raise MessageDecodeError(
                f"Expected to read 8 bytes, got {len(data)} bytes instead"
            )

        return struct.unpack('<q', data)[0]


class Float(Field):
    max_value = MAX_FLOAT
    wire_type = WireType.FIXED_32

    def encode_value(self, value) -> bytes:
        return struct.pack('<f', value)

    def decode(self, stream: IO):
        data = stream.read(4)

        if len(data) < 4:
            raise MessageDecodeError(
                f'Expected to read 4 bytes, got {len(data)} bytes instead'
            )

        return struct.unpack('<f', data)[0]

    def validate_value(self, value):
        if not (
            isinstance(value, float)
            or
            isinstance(value, int)
        ):
            raise ValueError(
                f"Expected a value of type 'float' or 'int'"
                f", got value of type {type(value).__name__!r} instead"
            )

        # we cannot compare negative float numbers to min float value
        # because 0 < sys.float_info.min < 1
        if value < 0:
            return

        if value > self.max_value:
            raise ValueError(
                f'Value {value!r} is greater than max value {self.max_value!r} '
                f'of type {type(self).__name__!r}'
            )


class Double(Float):
    max_value = MAX_DOUBLE
    wire_type = WireType.FIXED_64

    def encode_value(self, value) -> bytes:
        return struct.pack('<d', value)

    def decode(self, stream: IO):
        data = stream.read(8)

        if len(data) < 8:
            raise MessageDecodeError(
                f'Expected to read 8 bytes, got {len(data)} bytes instead'
            )

        return struct.unpack('<d', data)[0]


class MapField(Field):
    wire_type = WireType.LENGTH
    valid_key_fields = {
        Int32,
        Int64,
        SInt32,
        SInt64,
        UInt32,
        UInt64,
        Fixed32,
        Fixed64,
        SFixed32,
        SFixed64,
        String,
        Bool,
    }

    def __init__(
        self,
        key: Type[Field],
        value: Union[Type[Field], Type[enum.IntEnum], Type['Message']],
        *,
        number: int
    ):
        if key not in self.valid_key_fields:
            raise TypeError(
                'MapField key should be a scalar field except float, double and bytes'
            )

        super().__init__(number=number)

        key_field = key(number=1, required=True)

        from protox import Message

        if issubclass(value, Message):
            value_field = value.as_field(number=2, required=True)
        elif issubclass(value, enum.IntEnum):
            value_field = EnumField(number=2, required=True, py_enum=value)
        else:
            value_field = value(number=2, required=True)

        class _DictEntry(Message):
            key = key_field
            value = value_field

        self._dict_entry = _DictEntry
        self._key_field = key_field
        self._value_field = value_field

    @property
    def key_field(self) -> Field:
        return self._key_field

    @property
    def value_field(self) -> Field:
        return self._value_field

    def encode_value(self, value: Dict) -> bytes:
        buffer = bytearray()

        for key, value in value.items():
            buffer += self.header + encode_bytes(
                self._dict_entry(
                    key=key,
                    value=value
                ).to_bytes()
            )

        return bytes(buffer)

    encode = encode_value

    def decode(self, stream: BinaryIO) -> Tuple:
        entry = self._dict_entry.from_bytes(
            decode_bytes(stream)
        )
        return entry.key, entry.value

    def validate_value(self, value: Dict):
        if not isinstance(value, dict):
            raise ValueError(
                f'Map field should be a Dict-like object, got {type(value).__name__!r} instead'
            )


class MessageField(Field):
    wire_type = WireType.LENGTH

    def __init__(
        self,
        of_type,
        *,
        number,
        default=None,
        required=False,
    ):
        super().__init__(
            number=number,
            default=default,
            required=required,
        )
        self._of_type = of_type

    def encode_value(self, value) -> bytes:
        encoded_message = value.to_bytes()
        return encode_bytes(encoded_message)

    def decode(self, stream: IO):
        length = decode_varint(stream)
        message_stream = io.BytesIO(stream.read(length))
        return self._of_type.from_stream(message_stream)

    def validate_value(self, value):
        if not isinstance(value, self._of_type):
            raise ValueError(
                f'Expected a value of type {self._of_type.__name__!r}'
                f', got value of type {type(value).__name__!r} instead'
            )


class OneOf:
    def __init__(self, *args: str):
        self._fields: List[str] = list(args)

        # name of one_of is set in the message that contains the one_of
        self.name: Optional[str] = None

    @property
    def fields(self):
        return self._fields


one_of = OneOf

field_by_name: Dict[str, Field] = {
    'int32': Int32,
    'int64': Int64,
    'sint32': SInt32,
    'sint64': SInt64,
    'uint32': UInt32,
    'uint64': UInt64,
    'fixed32': Fixed32,
    'fixed64': Fixed64,
    'sfixed32': SFixed32,
    'sfixed64': SFixed64,
    'float': Float,
    'double': Double,
    'bytes': Bytes,
    'string': String,
    'bool': Bool,
    'enum': EnumField,
}

fields: List[Field] = list(field_by_name.values())
