import enum
from abc import ABC, abstractmethod
from typing import Type, Optional, List, Dict, Tuple, Iterable, Union, Any

from protox_encoding import (
    encode_varint, decode_varint,
    encode_bytes, decode_bytes,
    encode_int64, decode_int64,
    encode_uint32, decode_uint32,
    encode_uint64, decode_uint64,
    encode_sint32, decode_sint32,
    encode_sint64, decode_sint64,
    encode_float, decode_float,
    encode_double, decode_double,
    encode_bool, decode_bool,
    encode_string, decode_string,
    encode_fixed32, decode_fixed32,
    encode_fixed64, decode_fixed64,
    encode_sfixed32, decode_sfixed32,
    encode_sfixed64, decode_sfixed64,
    read_bytes,
)

from protox.constants import (
    MIN_INT32, MAX_INT32, MIN_INT64, MAX_INT64, MIN_UINT32,
    MAX_UINT32, MAX_UINT64, MIN_UINT64, MAX_FLOAT, MAX_DOUBLE
)
from protox.exceptions import MessageDecodeError, FieldValidationError

if False:
    from protox.message import Message  # noqa

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
    'PrimitiveField',

    'field_type_by_name',
    'field_types',
]


class WireType(enum.IntEnum):
    VARINT = 0
    FIXED_64 = 1
    LENGTH = 2
    START_GROUP = 3  # Will not be implemented. Deprecated by protobuf
    END_GROUP = 4  # Will not be implemented. Deprecated by protobuf
    FIXED_32 = 5


def _validate_field_number(number):
    if number not in range(1, 2 ** 29) or number in range(19_000, 20_000):
        raise FieldValidationError(
            'Field number {} is invalid. '
            'A valid field number should be in range [1..2 ** 29 -1] '
            'excluding range [19_000..19_999] '
            'which is reserved for the protobuf implementation'
        )


class Field(ABC):
    wire_type: WireType  # provided by subclasses
    number: int
    header: bytes

    def __init__(self, *, number: int):
        _validate_field_number(number)
        self.number = number
        self.header = encode_varint(self.number << 3 | self.wire_type)
        # name is set when adding the field to the message
        self.name: Optional[str] = None

    def read_to_dict(
        self,
        data: bytes,
        position: int,
        message_dict: dict
    ) -> int:
        item, position = self.decode(data, position)
        message_dict[self.name] = item

        return position

    def encode_value(self, value) -> bytes:
        raise NotImplementedError()

    def encode(self, value) -> bytes:
        """
        Encode value with header
        """
        return self.header + self.encode_value(value)

    def decode(self, buffer: bytes, position: int):
        raise NotImplementedError()

    def validate_value(self, value):
        raise NotImplementedError()


class PrimitiveField(Field, ABC):
    encoder: callable
    decoder: callable

    def __init__(
        self,
        *,
        number: int,
        default=None,
        required=False,
    ):
        super().__init__(number=number)
        self.default = default
        self.required = required

        if hasattr(self, 'encoder'):
            self.encode_value = self.encoder

        if hasattr(self, 'decoder'):
            self.decode = self.decoder

    @classmethod
    def as_repeated(
        cls,
        *,
        number: int,
        packed: bool = False,
    ) -> 'Repeated':
        return Repeated(
            of_type=cls,
            number=number,
            packed=packed,
        )


class BaseRepeatedStrategy(ABC):
    def __init__(self, repeated_field: 'Repeated', field: Field, number: int):
        self.repeated_field = repeated_field
        self.field = field
        self.number = number
        self.header = encode_varint(self.field.number << 3 | WireType.LENGTH)

    @abstractmethod
    def encode(self, values: list) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def decode(self, buffer: bytes, position: int):
        raise NotImplementedError()


class PackedRepeatedStrategy(BaseRepeatedStrategy):
    wire_type = WireType.LENGTH

    def read_to_dict(
        self,
        data: bytes,
        position: int,
        message_dict: dict
    ) -> int:
        item, position = self.decode(data, position)
        message_dict[self.repeated_field.name] = item

        return position

    def encode(self, values: list) -> bytes:
        if not values:
            return b''

        data = []

        for item in values:
            data.append(self.field.encode_value(item))

        return (
            self.header +
            encode_bytes(b''.join(data))
        )

    def decode(self, buffer: bytes, position: int):
        length, position = decode_varint(buffer, position)

        items = []

        if len(buffer) < position + length:
            raise MessageDecodeError(
                f'Expected to read {length:_} bytes'
            )

        end = position + length

        while position < end:
            item, position = self.field.decode(buffer, position)
            items.append(item)

        return items, position


class UnpackedRepeatedStrategy(BaseRepeatedStrategy):
    def read_to_dict(
        self,
        data: bytes,
        position: int,
        message_dict: dict
    ) -> int:
        item, position = self.decode(data, position)
        message_dict.setdefault(self.repeated_field.name, []).append(item)

        return position

    @property
    def wire_type(self):
        return self.field.wire_type

    def encode(self, values: list) -> bytes:
        if not values:
            return b''

        data = bytearray()

        for item in values:
            data += self.field.header + self.field.encode_value(item)

        return data

    def decode(self, buffer: bytes, position: int):
        """
        From docs:
        "repeated values do not have to appear consecutively;
        they may be interleaved with other fields."

        That's why we can only read exactly one item at a time
        """
        return self.field.decode(buffer, position)


class Repeated(Field):
    def __init__(
        self,
        of_type: Union[Type['Message'], Type[enum.IntEnum], Type[Field]],
        *,
        number: int,
        packed: bool = False
    ):
        from .message import Message

        if issubclass(of_type, Message):
            if packed:
                raise FieldValidationError(
                    f'Field of type {of_type.__name__!r}. Packed repeated fields only support primitive types'
                )
            self.field = MessageField(of_type, number=number)
        elif issubclass(of_type, enum.IntEnum):
            self.field = EnumField(of_type, number=number)
        else:
            self.field = of_type(number=number)

        self.of_type = of_type
        self.packed: bool = packed
        self.strategy: BaseRepeatedStrategy

        if packed:
            self.strategy = PackedRepeatedStrategy(self, self.field, number)
        else:
            self.strategy = UnpackedRepeatedStrategy(self, self.field, number)

        self.read_to_dict = self.strategy.read_to_dict
        self.wire_type = self.strategy.wire_type

        super().__init__(number=number)

    def encode(self, values: list) -> bytes:
        return self.strategy.encode(values)

    def encode_value(self, values: list) -> bytes:
        return self.strategy.encode(values)

    def decode(self, buffer: bytes, position: int):
        return self.strategy.decode(buffer, position)

    def validate_value(self, values: Iterable):
        if not isinstance(values, Iterable):
            raise ValueError(
                f'Repeated field {self.name!r} should be a \'list\' or \'tuple\', got {type(values).__name__!r} instead'
            )

        for value in values:
            self.field.validate_value(value)


class Int(PrimitiveField, ABC):
    min_value: int
    max_value: int
    wire_type = WireType.VARINT

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


class Int32(Int):
    min_value: int = MIN_INT32
    max_value: int = MAX_INT32

    # according to protobuf reference implementation
    # int32 encoded the same as int64
    encoder = encode_int64
    decoder = decode_int64


class Int64(Int):
    min_value: int = MIN_INT64
    max_value: int = MAX_INT64

    encoder = encode_int64
    decoder = decode_int64


class UInt32(Int):
    min_value: int = MIN_UINT32
    max_value: int = MAX_UINT32

    encoder = encode_uint32
    decoder = decode_uint32


class UInt64(Int):
    min_value: int = MIN_UINT64
    max_value: int = MAX_UINT64

    encoder = encode_uint64
    decoder = decode_uint64


class SInt32(Int):
    min_value: int = MIN_INT32
    max_value: int = MAX_INT32

    encoder = encode_sint32
    decoder = decode_sint32


class SInt64(Int):
    min_value: int = MIN_INT64
    max_value: int = MAX_INT64

    encoder = encode_sint64
    decoder = decode_sint64


class Bytes(PrimitiveField):
    wire_type = WireType.LENGTH

    encoder = encode_bytes
    decoder = decode_bytes

    def validate_value(self, value: bytes):
        if not isinstance(value, bytes):
            raise ValueError(
                f"Expected a value of type 'bytes', "
                f"got {type(value).__name__!r} instead"
            )


class String(PrimitiveField):
    wire_type = WireType.LENGTH
    encoder = encode_string
    decoder = decode_string

    def validate_value(self, value: str):
        if not isinstance(value, str):
            raise ValueError(
                f"Expected a value of type 'str', "
                f"got {type(value).__name__!r} instead"
            )


class Bool(PrimitiveField):
    wire_type = WireType.VARINT

    encoder = encode_bool
    decoder = decode_bool

    def validate_value(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(
                f"Expected a value of type 'bool', "
                f"got {type(value).__name__!r} instead"
            )


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


class EnumField(PrimitiveField):
    wire_type = WireType.VARINT

    def __init__(
        self,
        py_enum: Type[enum.IntEnum],
        *,
        number,
        default=None,
        required=False,
    ):
        _validate_py_enum(py_enum)

        super().__init__(
            number=number,
            default=default,
            required=required,
        )

        self.py_enum: Type[enum.IntEnum] = py_enum

    def encode_value(self, value: int) -> bytes:
        return encode_varint(value)

    def decode(self, buffer: bytes, position: int) -> Tuple[Optional[int], int]:
        value, position = decode_varint(buffer, position)

        # Specification: omit value that's not in the enum's variants
        try:
            rv = self.py_enum(value)
        except ValueError:
            rv = None

        return rv, position

    def validate_value(self, value: int):
        try:
            self.py_enum(value)
        except ValueError:
            raise ValueError(
                f'Expected an enum value of {repr([x for x in self.py_enum])}, '
                f'got {value} instead'
            )


class Fixed32(Int):
    min_value = MIN_UINT32
    max_value = MAX_UINT32
    wire_type = WireType.FIXED_32

    encoder = encode_fixed32
    decoder = decode_fixed32


class Fixed64(Int):
    min_value = MIN_UINT64
    max_value = MAX_UINT64
    wire_type = WireType.FIXED_64

    encoder = encode_fixed64
    decoder = decode_fixed64


class SFixed32(Int):
    min_value = MIN_INT32
    max_value = MAX_INT32
    wire_type = WireType.FIXED_32

    encoder = encode_sfixed32
    decoder = decode_sfixed32


class SFixed64(Int):
    min_value = MIN_INT64
    max_value = MAX_INT64
    wire_type = WireType.FIXED_64

    encoder = encode_sfixed64
    decoder = decode_sfixed64


class Float(PrimitiveField):
    max_value = MAX_FLOAT
    wire_type = WireType.FIXED_32

    encoder = encode_float
    decoder = decode_float

    def validate_value(self, value: Union[float, int]):
        if not isinstance(value, (float, int)):
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

    encoder = encode_double
    decoder = decode_double


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
        key: Union[Type[Int], Type[String]],
        value: Union[Type[PrimitiveField], Type[enum.IntEnum], Type['Message']],
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

        self.dict_entry = _DictEntry
        self.key_field = key_field
        self.value_field = value_field

    def read_to_dict(
        self,
        data: bytes,
        position: int,
        message_dict: dict
    ) -> int:
        key, value, position = self.decode(data, position)
        message_dict.setdefault(self.name, {})[key] = value

        return position

    def encode_value(self, value: Dict) -> bytes:
        buffer = bytearray()

        for key, value in value.items():
            buffer += self.header + encode_bytes(
                self.dict_entry(
                    key=key,
                    value=value
                ).to_bytes()
            )

        return bytes(buffer)

    encode = encode_value

    def decode(
        self,
        buffer: bytes,
        position: int
    ) -> Tuple:
        data, position = decode_bytes(buffer, position)
        entry = self.dict_entry.from_bytes(data)
        return entry.key, entry.value, position

    def validate_value(self, value: Dict):
        if not isinstance(value, dict):
            raise ValueError(
                f'Map field should be a Dict-like object, got {type(value).__name__!r} instead'
            )


class MessageField(Field):
    wire_type = WireType.LENGTH

    def __init__(
        self,
        of_type: Type['Message'],
        *,
        number: int,
        required: bool = False
    ):
        super().__init__(number=number)
        self.of_type: Type['Message'] = of_type
        self.required: bool = required

    def encode_value(self, value) -> bytes:
        encoded_message = value.to_bytes()
        return encode_bytes(encoded_message)

    def decode(self, buffer: bytes, position: int) -> Tuple[Any, int]:
        length, position = decode_varint(buffer, position)
        data, position = read_bytes(buffer, position, length)
        return self.of_type.from_bytes(data), position

    def validate_value(self, value):
        if not isinstance(value, self.of_type):
            raise ValueError(
                f'Expected a value of type {self.of_type.__name__!r}'
                f', got value of type {type(value).__name__!r} instead'
            )


class OneOf:
    def __init__(self, *args: str):
        self.fields: List[str] = list(args)

        # name of one_of is set in the message that contains the one_of
        self.name: Optional[str] = None


one_of = OneOf

field_type_by_name: Dict[str, Field] = {
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

field_types: List[Field] = list(field_type_by_name.values())
