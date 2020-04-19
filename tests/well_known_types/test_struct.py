import pytest

from protox import Struct, Message


def test_struct_message():
    struct = Struct()
    struct['number'] = 1
    struct['null'] = None
    struct['list'] = [1, 2, 3]

    assert 'number' in struct
    assert struct['number'] == 1
    assert 'bad_key' not in struct

    assert Struct.from_bytes(struct.to_bytes()) == struct


def test_struct_field():
    class MyMessage(Message):
        data: Struct = Struct.as_field(number=1)

    m = MyMessage(
        data=Struct(a=1, b='hello', c=[1, 2, 3])
    )
    assert MyMessage.from_bytes(m.to_bytes()) == m


def test_equals():
    a = Struct(x=123)
    b = Struct()
    assert a != b
    del a['x']
    assert a == b


def test_invalid_value():
    s = Struct()

    with pytest.raises(ValueError):
        s[1] = 'value'

    with pytest.raises(ValueError):
        s['hello'] = object()
