import io
from enum import IntEnum
from typing import Type

import pytest

from protox.encoding import decode_varint, encode_varint, decode_header
from protox.exceptions import MessageDecodeError, FieldValidationError
from protox.fields import (
    Int32, Int64, Bytes, UInt32, UInt64, String,
    Bool, SInt64, SInt32, EnumField, Fixed32, Fixed64, SFixed32,
    SFixed64, Float, Double, Field, Repeated
)


def test_encode_header():
    assert Int32(number=1).header == b'\x08'


uint32_bad_input = [
    b'',
    b'\x80\x80\x80',
    b'\xff\xff\xff',
]

uint32_test_cases = [
    (0, b'\x00'),
    (1, b'\x01'),
    (2, b'\x02'),
    (2147483647, b'\xff\xff\xff\xff\x07'),
]


class TestUInt32:
    @pytest.mark.parametrize('value, expected_value', uint32_test_cases)
    def test_encode(self, value, expected_value):
        assert UInt32(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', uint32_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert UInt32(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('bad_input', uint32_bad_input)
    def test_decode_bad_input(self, bad_input):
        stream = io.BytesIO(bad_input)

        with pytest.raises(MessageDecodeError):
            UInt32(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        0,
        1,
        13,
        2 ** 10,
        2 ** 32 - 1,
    ])
    def test_valid_input(self, valid_input):
        UInt32(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        -1,
        2 ** 40,
        '',
        []
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            UInt32(number=1).validate_value(invalid_input)


uint64_test_cases = uint32_test_cases + [
    (2 ** 64 - 1, b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01')
]


class TestUInt64:
    @pytest.mark.parametrize('value, expected_value', uint64_test_cases)
    def test_encode(self, value, expected_value):
        assert UInt64(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', uint64_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert UInt64(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('bad_input', uint32_bad_input)
    def test_decode_bad_input(self, bad_input):
        stream = io.BytesIO(bad_input)

        with pytest.raises(MessageDecodeError):
            UInt32(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        0,
        1,
        13,
        2 ** 10,
        2 ** 32 - 1,
        2 ** 64 - 1
    ])
    def test_valid_input(self, valid_input):
        UInt64(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        -1,
        2 ** 70,
        '',
        []
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            UInt64(number=1).validate_value(invalid_input)


int32_test_cases = uint32_test_cases + [
    (-2, b'\xfe\xff\xff\xff\xff\xff\xff\xff\xff\x01'),
    (-1, b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01'),
    (-2147483648, b'\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01'),
]


class TestInt32:
    @pytest.mark.parametrize('value, expected_value', int32_test_cases)
    def test_encode(self, value, expected_value):
        encoded_value = Int32(number=1).encode_value(value)

        assert encoded_value == expected_value

    @pytest.mark.parametrize('expected_value, value', int32_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        decoded_value = Int32(number=1).decode(stream)

        assert decoded_value == expected_value

    @pytest.mark.parametrize('bad_input', uint32_bad_input)
    def test_decode_bad_input(self, bad_input):
        stream = io.BytesIO(bad_input)

        with pytest.raises(MessageDecodeError):
            Int32(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        -2 ** 31,
        -1,
        0,
        1,
        10,
        2 ** 31 - 1,
    ])
    def test_valid_input(self, valid_input):
        Int32(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        - 2 ** 32,
        2 ** 32,
        "bad_input_type"
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Int32(number=1).validate_value(invalid_input)


int64_test_cases = int32_test_cases + [
    (-9223372036854775808, b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01'),
    (9223372036854775807, b'\xff\xff\xff\xff\xff\xff\xff\xff\x7f'),
]


class TestInt64:
    @pytest.mark.parametrize('value, expected_value', int64_test_cases)
    def test_encode(self, value, expected_value):
        encoded_value = Int64(number=1).encode_value(value)
        assert encoded_value == expected_value

    @pytest.mark.parametrize('expected_value, value', int64_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        decoded_value = Int64(number=1).decode(stream)
        assert decoded_value == expected_value

    @pytest.mark.parametrize('invalid_value', uint32_bad_input)
    def test_decode_invalid_value(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            Int64(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        -2 ** 63,
        -1,
        0,
        1,
        10,
        2 ** 63 - 1,
    ])
    def test_valid_input(self, valid_input):
        Int64(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        - 2 ** 64,
        2 ** 64,
        "bad_input_type"
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Int64(number=1).validate_value(invalid_input)


sint32_test_cases = [
    (-1, b'\x01'),
    (0, b'\x00'),
    (1, b'\x02'),
    (2, b'\x04'),
    (2 ** 31 - 1, b'\xfe\xff\xff\xff\x0f'),
    (-2 ** 31, b'\xff\xff\xff\xff\x0f'),
]


class TestSInt32:
    @pytest.mark.parametrize('value, expected_value', sint32_test_cases)
    def test_encode(self, value, expected_value):
        encoded_value = SInt32(number=1).encode_value(value)

        assert encoded_value == expected_value

    @pytest.mark.parametrize('expected_value, value', sint32_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        decoded_value = SInt32(number=1).decode(stream)

        assert decoded_value == expected_value

    @pytest.mark.parametrize('bad_input', uint32_bad_input)
    def test_decode_bad_input(self, bad_input):
        stream = io.BytesIO(bad_input)

        with pytest.raises(MessageDecodeError):
            SInt32(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        -2 ** 31,
        -1,
        0,
        1,
        10,
        2 ** 31 - 1,
    ])
    def test_valid_input(self, valid_input):
        SInt32(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        - 2 ** 32,
        2 ** 32,
        "bad_input_type"
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            SInt32(number=1).validate_value(invalid_input)


sint64_test_cases = sint32_test_cases + [
    (2 ** 63 - 1, b'\xfe\xff\xff\xff\xff\xff\xff\xff\xff\x01'),
    (-2 ** 63, b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01')
]


class TestSInt64:
    @pytest.mark.parametrize('value, expected_value', sint64_test_cases)
    def test_encode(self, value, expected_value):
        encoded_value = SInt64(number=1).encode_value(value)

        assert encoded_value == expected_value

    @pytest.mark.parametrize('expected_value, value', sint64_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        decoded_value = SInt64(number=1).decode(stream)

        assert decoded_value == expected_value

    @pytest.mark.parametrize('bad_input', uint32_bad_input)
    def test_decode_bad_input(self, bad_input):
        stream = io.BytesIO(bad_input)

        with pytest.raises(MessageDecodeError):
            SInt64(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        -2 ** 63,
        -1,
        0,
        1,
        10,
        2 ** 63 - 1,
    ])
    def test_valid_input(self, valid_input):
        SInt64(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        - 2 ** 64,
        2 ** 64,
        "bad_input_type"
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            SInt64(number=1).validate_value(invalid_input)


class TestBytes:
    @pytest.mark.parametrize('data', [
        b'',
        b'\x08',
        b'\x08' * 10,
    ])
    def test_encode_decode(self, data):
        encoded = Bytes(number=1).encode_value(data)
        stream = io.BytesIO(encoded)
        length = decode_varint(stream)
        assert length == len(data)

        stream.seek(0)
        decoded_data = Bytes(number=1).decode(stream)
        assert decoded_data == data

    @pytest.mark.parametrize('bad_input', [
        [],
        [3],
        [3, 1],
        [3, 1, 2]
    ])
    def test_decode_bad_input(self, bad_input):
        stream = io.BytesIO(bytes(bad_input))

        with pytest.raises(MessageDecodeError):
            Bytes(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        b'',
        b'\0x08',
        b'\0x08' * 10,
    ])
    def test_valid_input(self, valid_input):
        Bytes(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        [],
        123,
        'hello',
        True,
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Bytes(number=1).validate_value(invalid_input)


str_test_cases = [
    ('', b'\x00'),
    ('abc', b'\x03abc'),
    ('абв', b'\x06\xd0\xb0\xd0\xb1\xd0\xb2'),
]


class TestString:
    @pytest.mark.parametrize('value, expected_value', str_test_cases)
    def test_encode(self, value, expected_value):
        assert String(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', str_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert String(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('valid_input', [
        '',
        'abc',
        'абвгд',
    ])
    def test_valid_input(self, valid_input):
        String(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        [],
        b'',
        1,
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            String(number=1).validate_value(invalid_input)


bool_test_cases = [
    (True, b'\x01'),
    (False, b'\x00'),
]


class TestBool:
    @pytest.mark.parametrize('value, expected_value', bool_test_cases)
    def test_encode(self, value, expected_value):
        assert Bool(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', bool_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert Bool(number=1).decode(stream) is expected_value

    @pytest.mark.parametrize('valid_input', [
        True,
        False,
    ])
    def test_valid_input(self, valid_input):
        Bool(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        1,
        'a string',
        []
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Bool(number=1).validate_value(invalid_input)


@pytest.fixture(scope='session')
def color_enum():
    class Color(IntEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    return Color


@pytest.fixture(scope='session')
def color_field(color_enum):
    return EnumField(color_enum, number=1)


class TestEnum:
    def test_encode_decode(self, color_enum, color_field):
        encoded = color_field.encode_value(color_enum.RED)
        stream = io.BytesIO(encoded)
        decoded = color_field.decode(stream)

        assert decoded == color_enum.RED

    def test_decode_omits_unknown_variants(self, color_field):
        stream = io.BytesIO(encode_varint(999_999))

        assert color_field.decode(stream) is None

    @pytest.mark.parametrize('valid_input', [1, 2, 3])
    def test_valid_input(self, color_field, valid_input):
        color_field.validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [10, '10', []])
    def test_invalid_input(self, color_field, invalid_input):
        with pytest.raises(ValueError):
            color_field.validate_value(invalid_input)

    def test_bad_py_enum(self):
        with pytest.raises(FieldValidationError):
            EnumField(list, number=1, )

    @pytest.mark.parametrize('invalid_variant', [
        -2 ** 32,
        2 ** 32,
    ])
    def test_invalid_enum_variant(self, invalid_variant):
        with pytest.raises(FieldValidationError):
            class PyEnum(IntEnum):
                X = invalid_variant

            EnumField(PyEnum, number=1)

    @pytest.mark.parametrize('valid_variant', [
        -2 ** 31,
        2 ** 31 - 1,
    ])
    def test_valid_enum_variant(self, valid_variant):
        class PyEnum(IntEnum):
            X = valid_variant

        EnumField(PyEnum, number=1)


fixed32_test_cases = [
    (0, b'\x00\x00\x00\x00'),
    (1, b'\x01\x00\x00\x00'),
    (2 ** 32 - 1, b'\xff\xff\xff\xff'),
]


class TestFixed32:
    @pytest.mark.parametrize('value, expected_value', fixed32_test_cases)
    def test_encode(self, value, expected_value):
        assert Fixed32(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', fixed32_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert Fixed32(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('invalid_value', [
        b'',
        b'\x00\x00',
    ])
    def test_decode_invalid(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            Fixed32(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        0,
        1,
        2 ** 32 - 1
    ])
    def test_valid_input(self, valid_input):
        Fixed32(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        -1,
        2 ** 32,
        "",
        [],
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Fixed32(number=1).validate_value(invalid_input)


fixed64_test_cases = [
    (0, b'\x00\x00\x00\x00\x00\x00\x00\x00'),
    (1, b'\x01\x00\x00\x00\x00\x00\x00\x00'),
    (2 ** 64 - 1, b'\xff\xff\xff\xff\xff\xff\xff\xff'),
]


class TestFixed64:
    @pytest.mark.parametrize('value, expected_value', fixed64_test_cases)
    def test_encode(self, value, expected_value):
        assert Fixed64(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', fixed64_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert Fixed64(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('invalid_value', [
        b'',
        b'\x00\x00',
    ])
    def test_decode_invalid(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            Fixed64(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        0,
        1,
        2 ** 64 - 1,
    ])
    def test_valid_input(self, valid_input):
        Fixed64(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        -1,
        2 ** 64,
        "",
        [],
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Fixed64(number=1).validate_value(invalid_input)


sfixed32_test_cases = [
    (-2 ** 31, b'\x00\x00\x00\x80'),
    (-1, b'\xff\xff\xff\xff'),
    (0, b'\x00\x00\x00\x00'),
    (1, b'\x01\x00\x00\x00'),
    (2 ** 31 - 1, b'\xff\xff\xff\x7f')
]


class TestSFixed32:
    @pytest.mark.parametrize('value, expected_value', sfixed32_test_cases)
    def test_encode(self, value, expected_value):
        assert SFixed32(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', sfixed32_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert SFixed32(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('invalid_value', [
        b'',
        b'\x00',
    ])
    def test_decode_invalid(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            SFixed32(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        -2 ** 31,
        -1,
        0,
        1,
        2 ** 31 - 1
    ])
    def test_valid_input(self, valid_input):
        SFixed32(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        -2 ** 32,
        2 ** 32,
        b"",
        []
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            SFixed32(number=1).validate_value(invalid_input)


sfixed64_test_cases = [
    (-2 ** 63, b'\x00\x00\x00\x00\x00\x00\x00\x80'),
    (-1, b'\xff\xff\xff\xff\xff\xff\xff\xff'),
    (0, b'\x00\x00\x00\x00\x00\x00\x00\x00'),
    (1, b'\x01\x00\x00\x00\x00\x00\x00\x00'),
    (2 ** 63 - 1, b'\xff\xff\xff\xff\xff\xff\xff\x7f'),
]


class TestSFixed64:
    @pytest.mark.parametrize('value, expected_value', sfixed64_test_cases)
    def test_encode(self, value, expected_value):
        assert SFixed64(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', sfixed64_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)

        assert SFixed64(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('invalid_value', [
        b'',
        b'\x00',
        b'\x00' * 4,
        b'\x00' * 7,
    ])
    def test_decode_invalid(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            SFixed64(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        -2 ** 63,
        -1,
        0,
        1,
        2 ** 63 - 1
    ])
    def test_valid_input(self, valid_input):
        SFixed64(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        -2 ** 64,
        2 ** 64,
        b'',
        []
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            SFixed64(number=1).validate_value(invalid_input)


float_test_cases = [
    (1.1754943508222875e-38, b'\x00\x00\x80\x00'),
    (-1, b'\x00\x00\x80\xbf'),
    (0, b'\x00\x00\x00\x00'),
    (1, b'\x00\x00\x80?'),
    (3.4028234663852886e+38, b'\xff\xff\x7f\x7f'),
]


class TestFloat:
    @pytest.mark.parametrize('value, expected_value', float_test_cases)
    def test_encode(self, value, expected_value):
        encoded_value = Float(number=1).encode_value(value)

        assert encoded_value == expected_value

    @pytest.mark.parametrize('expected_value, value', float_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        encoded_value = Float(number=1).decode(stream)

        assert encoded_value == expected_value

    @pytest.mark.parametrize('invalid_value', [
        b'',
        b'\x00',
        b'\xff\xff\x7f'
    ])
    def test_decode_invalid(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            Float(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        0,
        1,
        1.0,
        1.175494351e-38,
        3.402823466e+38,
    ])
    def test_valid_input(self, valid_input):
        Float(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        b'',
        [],
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Float(number=1).validate_value(invalid_input)


double_test_cases = [
    (2.2250738585072014e-308, b'\x00\x00\x00\x00\x00\x00\x10\x00'),
    (-1, b'\x00\x00\x00\x00\x00\x00\xf0\xbf'),
    (0, b'\x00\x00\x00\x00\x00\x00\x00\x00'),
    (1, b'\x00\x00\x00\x00\x00\x00\xf0?'),
    (1.7976931348623157e+308, b'\xff\xff\xff\xff\xff\xff\xef\x7f'),
]


class TestDouble:
    @pytest.mark.parametrize('value, expected_value', double_test_cases)
    def test_encode(self, value, expected_value):
        assert Double(number=1).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', double_test_cases)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        assert Double(number=1).decode(stream) == expected_value

    @pytest.mark.parametrize('invalid_value', [
        b'',
        b'\x00',
        b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF',
    ])
    def test_decode_invalid(self, invalid_value):
        stream = io.BytesIO(invalid_value)

        with pytest.raises(MessageDecodeError):
            Double(number=1).decode(stream)

    @pytest.mark.parametrize('valid_input', [
        2.2250738585072014e-308,
        -1.0,
        0.0,
        1.0,
        2.5,
        1.7976931348623158e+308,
    ])
    def test_valid_input(self, valid_input):
        Double(number=1).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        b'',
        [],
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Double(number=1).validate_value(invalid_input)


@pytest.mark.parametrize('field_type, expected_wire_type', [
    (Int32, 0),
    (Int64, 0),
    (SInt32, 0),
    (SInt64, 0),
    (UInt32, 0),
    (UInt64, 0),
    (Bytes, 2),
    (String, 2),
    (Bool, 0),
    (Fixed32, 5),
    (Fixed64, 1),
    (SFixed32, 5),
    (SFixed64, 1),
    (Float, 5),
    (Double, 1),
])
def test_field_header(field_type: Type[Field], expected_wire_type):
    assert field_type.wire_type == expected_wire_type

    field_number = 2 * 32
    encoded_header = field_type(number=field_number).header
    stream = io.BytesIO(encoded_header)
    number, wire_type = decode_header(stream)

    assert number == field_number
    assert wire_type == expected_wire_type


def test_enum_field_header(color_field):
    expected_wire_type = 0

    assert color_field.wire_type == expected_wire_type

    encoded_header = color_field.header

    stream = io.BytesIO(encoded_header)
    number, wire_type = decode_header(stream)

    assert number == color_field.number
    assert wire_type == expected_wire_type


repeated_test_cases = [
    ([], b''),
    ([1], b'\x08\x01'),
    ([1, 2, 3], b'\x08\x01\x08\x02\x08\x03'),
]


class TestRepeatedField:
    @pytest.mark.parametrize('value, expected_value', repeated_test_cases)
    def test_encode(self, value, expected_value):
        assert Repeated(Int32, number=1, packed=False).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', repeated_test_cases)
    def test_decode(self, value, expected_value):
        field = Repeated(Int32, number=1, packed=False)

        stream = io.BytesIO(value)

        data = []

        for _ in expected_value:
            decode_varint(stream)
            data.append(field.decode(stream))

        assert data == expected_value

    @pytest.mark.parametrize('valid_input', [
        [],
        [1],
        [1, 2, 3],
    ])
    def test_valid_input(self, valid_input):
        Repeated(Int32, number=1, packed=False).validate_value(valid_input)

    @pytest.mark.parametrize('invalid_input', [
        None,
        1,
        [None],
    ])
    def test_invalid_input(self, invalid_input):
        with pytest.raises(ValueError):
            Repeated(Int32, number=1, packed=False).validate_value(invalid_input)


packed_repeated_test_case = [
    ([1], b'\n\x01\x01'),
    ([1, 2, 3], b'\n\x03\x01\x02\x03'),
    ([0xff, 0xffff00, 0xffff], b'\n\t\xff\x01\x80\xfe\xff\x07\xff\xff\x03'),
]


class TestPackedRepeatedField:
    @pytest.mark.parametrize('value, expected_value', packed_repeated_test_case + [([], b'')])
    def test_encode(self, value, expected_value):
        assert Repeated(Int32, number=1, packed=True).encode_value(value) == expected_value

    @pytest.mark.parametrize('expected_value, value', packed_repeated_test_case)
    def test_decode(self, value, expected_value):
        stream = io.BytesIO(value)
        number, wire_type = decode_header(stream)

        assert number == 1
        assert wire_type == 2

        data = Repeated(Int32, number=1, packed=True).decode(stream)
        print('\n>>>', data)


class TestFieldNumber:
    @pytest.mark.parametrize('invalid_field_number', [-1, 0, 2 ** 29, 19_500])
    def test_invalid_field_number(self, invalid_field_number):
        with pytest.raises(FieldValidationError):
            Int32(number=invalid_field_number)

    @pytest.mark.parametrize('valid_field_number', [1, 2 ** 29 - 1])
    def test_valid_field_number(self, valid_field_number):
        Int32(number=valid_field_number)
