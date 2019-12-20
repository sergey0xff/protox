import pytest
from typing import List

from protox import Message, Repeated, Int32, String


@pytest.fixture(scope='function')
def user_message():
    class PhoneNumber(Message):
        number = String(number=1)

    class User(Message):
        numbers: List[int] = Repeated(Int32, number=1)
        phone_numbers: List[PhoneNumber] = Repeated(PhoneNumber, number=2)

    return User()


def test_valid_assignment(user_message):
    user_message.numbers = [1]


def test_invalid_assignment(user_message):
    with pytest.raises(ValueError):
        user_message.numbers = ["one"]


def test_valid_append(user_message):
    user_message.numbers.append(1)


def test_invalid_append(user_message):
    with pytest.raises(ValueError):
        user_message.numbers.append("one")


def test_valid_set_item(user_message):
    user_message.numbers = [1, 2, 3]
    user_message.numbers[0] = 1


def test_invalid_set_item(user_message):
    user_message.numbers = [1, 2, 3]

    with pytest.raises(ValueError):
        user_message.numbers[0] = "one"


def test_invalid_set_item_slice(user_message):
    user_message.numbers = [1, 2, 3]

    with pytest.raises(ValueError):
        user_message.numbers[:1] = ["one"]


def test_extend_with_valid_values(user_message):
    user_message.numbers.extend([1, 2, 3])

    assert user_message.numbers == [1, 2, 3]


def test_extend_with_invalid_values(user_message):
    user_message.numbers = [1, 2, 3]

    with pytest.raises(ValueError):
        user_message.numbers.extend([1, 2, "three"])
