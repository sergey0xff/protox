import io
from enum import IntEnum
from typing import List

import pytest

from protox import Empty
from protox.exceptions import FieldValidationError
from protox.fields import Int32, String, MessageField, one_of, EnumField, Repeated
from protox.message import Message


@pytest.fixture(scope='session')
def simple_message():
    class SimpleMessage(Message):
        x = Int32(number=1)

    return SimpleMessage(x=1)


@pytest.fixture(scope='session')
def simple_message_encoded():
    return b'\x08\x01'


def test_dumps(simple_message, simple_message_encoded):
    assert simple_message.to_bytes() == simple_message_encoded


def test_dump(simple_message, simple_message_encoded):
    stream = io.BytesIO()
    simple_message.to_stream(stream)
    stream.seek(0)

    assert stream.read() == simple_message_encoded


def test_load(simple_message, simple_message_encoded):
    stream = io.BytesIO(simple_message_encoded)
    message = simple_message.from_stream(stream)

    assert message.x == 1


def test_loads(simple_message, simple_message_encoded):
    message = simple_message.from_bytes(simple_message_encoded)

    assert message.x == 1


def test_default_value_encoding():
    class MyMessage(Message):
        x = Int32(number=1, default=100)
        y = Int32(number=2)

    encoded_message = MyMessage(y=200).to_bytes()
    message = MyMessage.from_bytes(encoded_message)
    expected_message = MyMessage(x=100, y=200)

    assert message.x == expected_message.x
    assert message.y == expected_message.y


def test_optional_fields():
    class MyMessage(Message):
        x = Int32(number=1, required=False)
        y = Int32(number=2, required=False)

    encoded_message = MyMessage().to_bytes()
    message = MyMessage.from_stream(io.BytesIO(encoded_message))

    expected_message = MyMessage()
    assert message.x == expected_message.x
    assert message.y == expected_message.y


def test_default_value():
    default_value = 777

    class MyMessage(Message):
        x: int = Int32(number=1, required=True)
        y: int = Int32(number=2, default=default_value)

    message = MyMessage()

    assert not message.has_field('x')
    assert message.x is None

    assert not message.has_field('y')
    assert message.y == default_value

    message.y = default_value
    assert message.has_field('y')


def test_embedded_message():
    class User(Message):
        name: str = String(number=1)

    class SimpleMessage(Message):
        user: User = MessageField(User, number=1)

    message = SimpleMessage(user=User(name='John Doe'))
    encoded_message = message.to_bytes()
    stream = io.BytesIO(encoded_message)

    decoded_message = SimpleMessage.from_stream(stream)

    assert decoded_message.user.name == message.user.name


def test_message_from_bytes():
    class User(Message):
        name: str = String(number=1)

    message = User(name='John Doe')
    encoded_message = message.to_bytes()
    decoded_message = User.from_bytes(encoded_message)

    assert decoded_message.name == message.name


def test_read_unknown_fields():
    class User(Message):
        name: str = String(number=1)

    class UserV2(Message):
        name: str = String(number=1)
        x: int = Int32(number=2)

    user = UserV2(name='John', x=123)
    encoded_user = user.to_bytes()

    decoded_user = User.from_bytes(encoded_user)
    assert decoded_user.name == user.name


def test_required_default_is_encoded():
    class RequiredDefault(Message):
        number: int = Int32(number=1, default=123, required=True)

    encoded = RequiredDefault().to_bytes()
    assert len(encoded) > 1


def test_optional_default_is_encoded():
    class OptionalDefault(Message):
        number: int = Int32(number=1, default=123, required=True)

    encoded = OptionalDefault().to_bytes()
    assert len(encoded) > 1


class TestEnum:
    def test_message_not_set_value_is_none(self):
        class Color(IntEnum):
            GREEN = 1

        class EnumMessage(Message):
            color: Color = EnumField(Color, number=1)

        message = EnumMessage()
        assert message.color is None

    def test_enum_default_value(self):
        class Color(IntEnum):
            GREEN = 1
            RED = 2

        default_value = Color.GREEN

        class EnumMessage(Message):
            color: Color = EnumField(Color, number=1, default=default_value)

        message = EnumMessage()
        assert message.color is default_value

    def test_enum_decoded_value(self):
        class Color(IntEnum):
            GREEN = 1

        class EnumMessage(Message):
            color: Color = EnumField(Color, number=1)

        message = EnumMessage(color=Color.GREEN)
        new_message = EnumMessage.from_bytes(message.to_bytes())

        assert new_message.color == Color.GREEN
        assert isinstance(new_message.color, Color)


class TestRepeatedField:
    def test_empty_unpacked_repeated_field(self):
        class UnpackedRepeatedMessage(Message):
            numbers: List[int] = Repeated(Int32, number=1, packed=False)

        message = UnpackedRepeatedMessage(numbers=[])
        encoded_message = message.to_bytes()
        decoded_message = UnpackedRepeatedMessage.from_bytes(encoded_message)

        assert len(decoded_message.numbers) == 0

    def test_unpacked_repeated_field(self):
        class UnpackedRepeatedMessage(Message):
            numbers: List[int] = Repeated(Int32, number=1, packed=False)

        numbers = [1, 2, 3]

        message = UnpackedRepeatedMessage(numbers=numbers)
        encoded_message = message.to_bytes()
        decoded_message = UnpackedRepeatedMessage.from_bytes(encoded_message)

        assert decoded_message.numbers == numbers


@pytest.mark.parametrize('packed', [True, False])
def test_repeated_enum(packed):
    class Option(IntEnum):
        X = 1
        Y = 2
        Z = 3

    class PackedRepeatedEnum(Message):
        options = Repeated(Option, number=1, packed=packed)

    options = [Option.X, Option.Y, Option.Z]

    encoded = PackedRepeatedEnum(options=options).to_bytes()
    decoded = PackedRepeatedEnum.from_bytes(encoded)

    assert decoded.options == options


class TestOneOf:
    def test_settings_one_of_makes_other_fields_none(self):
        class OneOfMessage(Message):
            x: int = Int32(number=1, required=False)
            y: int = Int32(number=2, required=False)
            z: int = Int32(number=3, required=False)

            one_of_three = one_of('x', 'y', 'z')

        message = OneOfMessage(x=1, y=2, z=3)

        assert message.which_one_of('one_of_three') == 'z'

        assert message.x is None
        assert message.y is None
        assert message.z == 3

        message.y = 2
        assert message.which_one_of('one_of_three') == 'y'

        message.x = 1
        assert message.which_one_of('one_of_three') == 'x'

        assert message.x == 1
        assert message.y is None

        message = OneOfMessage.from_bytes(message.to_bytes())

        assert message.x == 1
        assert message.y is None

    def test_several_one_ofs_work_together(self):
        class OneOfMessage(Message):
            a: int = Int32(number=1, required=False)
            b: int = Int32(number=2, required=False)
            c: int = Int32(number=3, required=False)
            d: int = Int32(number=4, required=False)

            first_one_of = one_of('a', 'b')
            second_one_of = one_of('c', 'd')

        message = OneOfMessage(
            a=1,
            b=2,
            c=3,
            d=4,
        )

        assert message.which_one_of('first_one_of') == 'b'
        assert message.a is None
        assert message.b == 2

        assert message.which_one_of('second_one_of') == 'd'
        assert message.c is None
        assert message.d == 4

    def test_required_field(self):
        with pytest.raises(FieldValidationError):
            class _(Message):
                x: int = Int32(number=1, required=True)
                y: int = Int32(number=2, required=False)

                one_of_pair = one_of('x', 'y')

    def test_empty_one_of(self):
        class OneOfMessage(Message):
            x: int = Int32(number=1, required=False)
            y: int = Int32(number=2, required=False)

            one_of_pair = one_of('x', 'y')

        empty_message = OneOfMessage()
        empty_message.which_one_of('one_of_pair')

    def test_one_of_bad_field(self):
        class EmptyMessage(Message):
            pass

        empty_message = EmptyMessage()

        with pytest.raises(ValueError):
            empty_message.which_one_of('bad_one_of_field')

        class OneOfMessage(Message):
            x: int = Int32(number=1, required=False)
            y: int = Int32(number=2, required=False)

            one_of_pair = one_of('x', 'y')

        message = OneOfMessage()

        with pytest.raises(ValueError):
            message.which_one_of('bad_one_of_field')


def test_field_number_validation():
    with pytest.raises(FieldValidationError):
        class Point(Message):
            x = Int32(number=1)
            y = Int32(number=1)


def test_field_default_value_validation():
    with pytest.raises(FieldValidationError):
        class _(Message):
            x = Int32(number=1, default="123")


def test_one_of_with_zero_fields():
    with pytest.raises(FieldValidationError):
        class _(Message):
            number = one_of()


def test_one_of_with_one_field():
    class _(Message):
        x = Int32(number=1, required=False)
        number = one_of('x')


def test_message_as_field():
    class SimpleMessage(Message):
        x = Int32(number=1)

    number = 1
    message_field = SimpleMessage.as_field(number=number)
    assert isinstance(message_field, MessageField)
    assert message_field.number == number


def test_required_message_field():
    class SimpleMessage(Message):
        x = Empty.as_field(number=1, required=True)

    message = SimpleMessage()
    assert not message.is_initialized()

    message.x = Empty()
    assert message.is_initialized()


def test_optional_message_field():
    class SimpleMessage(Message):
        x = Empty.as_field(number=1, required=False)

    message = SimpleMessage()
    assert message.is_initialized()

    message.x = Empty()
    assert message.is_initialized()


def test_message_as_repeated():
    class SimpleMessage(Message):
        x = Int32(number=1)

    number = 1
    repeated_message_field = SimpleMessage.as_repeated(number=number)
    assert isinstance(
        repeated_message_field,
        Repeated
    )
    assert repeated_message_field.number == number


def test_message_constructor_raises_attribute_error():
    class SimpleMessage(Message):
        x = Int32(number=1)

    with pytest.raises(AttributeError):
        SimpleMessage(bad_field=123)


def test_message_constructor_raises_value_error():
    class SimpleMessage(Message):
        x = Int32(number=1)

    with pytest.raises(ValueError):
        SimpleMessage(x="string")


def test_is_initialized():
    class SimpleMessage(Message):
        x: int = Int32(number=1)
        y: int = Int32(number=2, required=True)

    message = SimpleMessage()
    assert not message.is_initialized()

    message.y = 2
    assert message.is_initialized()


def test_is_empty():
    class SimpleMessage(Message):
        x: int = Int32(number=1)

    message = SimpleMessage()
    assert message.is_empty()

    message.x = 123
    assert not message.is_empty()


def test_list_fields():
    class SimpleMessage(Message):
        x: int = Int32(number=1)

    assert SimpleMessage.list_fields() == ['x']


def test_equals():
    class SimpleMessage(Message):
        x: int = Int32(number=1)

    one = SimpleMessage(x=1)
    two = SimpleMessage(x=2)
    three = SimpleMessage(x=1)

    assert one != two
    assert not (one == two)
    assert one == three
    assert not (one != three)


def test_default_equals():
    class SimpleMessage(Message):
        x: int = Int32(number=1, default=0)

    assert SimpleMessage() == SimpleMessage(x=0)


def test_message_read_equals():
    class SimpleMessage(Message):
        x: int = Int32(number=1, default=0)

    a = SimpleMessage(x=0)
    b = SimpleMessage.from_bytes(a.to_bytes())

    assert a == b
