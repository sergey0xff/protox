from protox_encoding import decode_varint, decode_fixed64, decode_fixed32, decode_bytes


def _decode_group_start(_buffer: bytes, _position: int):
    # TODO: implement to discard old messages group fields
    raise NotImplementedError(
        'Groups are not supported [deprecated by protobuf]'
    )


def _decode_group_end(_buffer: bytes, _position: int):
    # TODO: implement to discard old messages group fields
    raise NotImplementedError(
        'Groups are not supported [deprecated by protobuf]'
    )


wire_type_to_decoder = {
    0: decode_varint,
    1: decode_fixed64,
    2: decode_bytes,
    3: _decode_group_start,
    4: _decode_group_end,
    5: decode_fixed32
}
