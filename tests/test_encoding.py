import io

import pytest

from protox.encoding import (
    decode_bytes, encode_varint, decode_varint, encode_zig_zag32,
    decode_zig_zag, encode_zig_zag64, encode_bytes
)
from protox.exceptions import MessageDecodeError


@pytest.mark.parametrize('value', [
    0,
    1,
    127,
    128,
    2 ** 32,
    2 ** 64,
])
def test_encode_decode_varint(value):
    encoded_value = encode_varint(value)
    stream = io.BytesIO(encoded_value)
    decoded_value = decode_varint(stream)

    assert decoded_value == value


@pytest.mark.parametrize('bad_input', [
    [],
    [128],
    [128, 128, 128]
])
def test_decode_varint_raises_on_eof(bad_input):
    encoded_value = bytes(bad_input)
    stream = io.BytesIO(encoded_value)

    with pytest.raises(MessageDecodeError):
        decode_varint(stream)


def test_decode_varint_raises_when_max_data_length_exceeded():
    bad_value = bytes([255] * 10 + [1])
    stream = io.BytesIO(bad_value)

    with pytest.raises(MessageDecodeError):
        decode_varint(stream)


@pytest.mark.parametrize('data', [
    b'',
    b'0',
    b'123' * 10_000
])
def test_encode_decode_bytes(data):
    encoded = encode_bytes(data)
    stream = io.BytesIO(encoded)
    bytes_read = decode_bytes(stream)

    assert bytes_read == data
    assert len(bytes_read) == len(data)


@pytest.mark.parametrize('string', [
    '',
    'a',
    'hello',
    'абвгд',
    'a' * 10_000,
])
def test_read_string(string):
    data = string.encode('utf-8')
    length = encode_varint(len(data))
    stream = io.BytesIO(length + data)

    bytes_read = decode_bytes(stream)
    assert bytes_read == data

    string_read = bytes_read.decode('utf-8')
    assert string_read == string


zig_zag32_test_cases = [
    (-1, 1),
    (-2, 3),
    (-3, 5),
    (1, 2),
    (2, 4),
    (3, 6),
]

zig_zag64_test_cases = [
    (2 ** 63 - 1, 18446744073709551614),
    (-2 ** 63, 18446744073709551615),
]


@pytest.mark.parametrize('value, expected_value', zig_zag32_test_cases)
def test_zig_zag32_encoding(value, expected_value):
    assert encode_zig_zag32(value) == expected_value


@pytest.mark.parametrize(
    'value, expected_value',
    zig_zag32_test_cases + zig_zag64_test_cases
)
def test_zig_zag64_encoding(value, expected_value):
    assert encode_zig_zag64(value) == expected_value


@pytest.mark.parametrize('expected_value, value', zig_zag32_test_cases)
def test_zig_zag_encoding(value, expected_value):
    assert decode_zig_zag(value) == expected_value
