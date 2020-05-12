import inspect
from typing import List, Type

import pytest

from protox import Message, String
from protox.mock import mock_message
from importlib import import_module


def _get_generated_messages() -> List[Type[Message]]:
    messages = []
    module_names = [
        'enums_pb',
        'message_pb',
        'primitive_values_pb',
    ]

    for module_name in module_names:
        module = import_module(
            f'tests.generated_messages.{module_name}'
        )

        for obj in [getattr(module, x) for x in dir(module)]:
            if inspect.isclass(obj) and issubclass(obj, Message):
                messages.append(obj)

    return messages


@pytest.mark.parametrize('message_type', _get_generated_messages())
def test_mock_with_generated_messages(message_type):
    message = mock_message(message_type)
    message_read = message_type.from_bytes(
        message.to_bytes()
    )
    assert message == message_read, f'{message._data}\n{message_read._data}'


def test_mock_message_with_default_values():
    class User(Message):
        name: str = String(number=1)

    name = 'John Doe'
    user = mock_message(
        User,
        name=name,
    )
    assert user.name == name
