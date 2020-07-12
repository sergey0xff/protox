import struct
from typing import IO, Tuple

from protox.exceptions import MessageDecodeError


def encode_bytes(data: bytes) -> bytes:
    length = encode_varint(len(data))
    return length + data


def decode_bytes(stream: IO) -> bytes:
    length = decode_varint(stream)
    data = stream.read(length)

    if len(data) < length:
        raise MessageDecodeError(
            f'Expected to read {length} bytes, {len(data)} bytes read instead'
        )

    return data


def encode_varint(value: int) -> bytes:
    rv = []
    x = value & 127
    value >>= 7

    while value:
        rv.append(x | 128)
        x = value & 127
        value >>= 7

    rv.append(x)

    return bytes(rv)


def decode_varint(stream: IO) -> int:
    rv = 0
    shift = 0

    for _ in range(10):
        x = stream.read(1)

        if x == b'':
            raise MessageDecodeError(
                'Unexpected end of stream when reading varint'
            )

        x = ord(x)
        rv |= (x & 127) << shift
        shift += 7

        if not x & 128:
            return rv

    raise MessageDecodeError(
        'Exceeded 10 bytes maximum length when reading varint'
    )


def encode_zig_zag32(x: int) -> int:
    return (x << 1) ^ (x >> 31)


def encode_zig_zag64(x: int) -> int:
    return (x << 1) ^ (x >> 63)


def decode_zig_zag(x: int) -> int:
    return (x >> 1) ^ -(x & 1)


def decode_header(stream) -> Tuple[int, int]:
    header = decode_varint(stream)
    return header >> 3, header & 0b111


def _decode_fixed64(stream):
    data = stream.read(8)

    if len(data) != 8:
        raise MessageDecodeError(
            f'Expected to read {8} bytes, got {len(data)} bytes instead'
        )

    return struct.unpack('<Q', data)[0]


def _decode_fixed32(stream):
    data = stream.read(4)

    if len(data) != 4:
        raise MessageDecodeError(
            f'Expected to read {4} bytes, got {len(data)} bytes instead'
        )

    return struct.unpack('<I', data)[0]


def _decode_group_start(stream):
    # TODO: implement to discard old messages group fields
    raise NotImplementedError(
        'Groups are not supported [deprecated by protobuf]'
    )


def _decode_group_end(stream):
    # TODO: implement to discard old messages group fields
    raise NotImplementedError(
        'Groups are not supported [deprecated by protobuf]'
    )


wire_type_to_decoder = {
    0: decode_varint,
    1: _decode_fixed64,
    2: decode_bytes,
    3: _decode_group_start,
    4: _decode_group_end,
    5: _decode_fixed32
}
