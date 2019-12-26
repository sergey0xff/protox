from enum import IntEnum
from typing import Dict

import pytest
import typing

from protox import Message, fields, MapField

map_test_cases = [
    (
        b'',
        {},
    ),
    (
        b'\n\x07\n\x03key\x10\x01',
        {'key': 1},
    ),
    (
        b'\n\t\n\x05value\x10\x02\n\x07\n\x03key\x10\x01',
        {'value': 2, 'key': 1},
    )
]


class MapMessage(Message):
    dictionary: Dict[str, int] = fields.MapField(
        fields.String,
        fields.Int32,
        number=1,
    )


class TestMapFields:
    @pytest.mark.parametrize('value, expected_value', map_test_cases)
    def test_decode(self, value: bytes, expected_value: dict):
        message = MapMessage.from_bytes(value)
        assert message.dictionary == expected_value

    @pytest.mark.parametrize('expected_value, value', map_test_cases)
    def test_encode(self, value: dict, expected_value: bytes):
        assert MapMessage(dictionary=value).to_bytes() == expected_value

    def test_field_invalid_value(self):
        with pytest.raises(ValueError):
            MapMessage(dictionary=123)

        message = MapMessage()

        with pytest.raises(ValueError):
            message.dictionary = 123

    def test_invalid_key(self):
        with pytest.raises(ValueError):
            MapMessage(dictionary={None: 123})

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            MapMessage(dictionary={'hello': None})

    @pytest.mark.parametrize('key_field', MapField.valid_key_fields)
    def test_valid_key_types(self, key_field):
        MapField(
            key=key_field,
            value=fields.String,
            number=1
        )

    @pytest.mark.parametrize('invalid_key_field', [
        fields.Bytes,
        fields.Float,
        fields.Double,
        fields.MessageField,
        fields.EnumField,
    ])
    def test_invalid_key_types(self, invalid_key_field):
        with pytest.raises(TypeError):
            MapField(
                key=invalid_key_field,
                value=fields.String,
                number=1
            )

    def test_enum_values(self):
        class MyMessage(Message):
            class Color(IntEnum):
                RED = 1
                GREEN = 2
                BLUE = 3

            map: typing.Dict[str, Color] = fields.MapField(
                key=fields.String,
                value=Color,
                number=1
            )

        message = MyMessage()
        assert message.map == {}
        message.map['color'] = MyMessage.Color.BLUE
        assert message.map == {'color': MyMessage.Color.BLUE}

        new_message = MyMessage.from_bytes(message.to_bytes())
        assert new_message.map == {'color': MyMessage.Color.BLUE}


