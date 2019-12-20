from protox import Message, Int32
from protox.message import define_fields


def test_add_fields_to_message():
    class User(Message):
        id: int

    define_fields(
        User,
        id=Int32(number=1),
    )
    user_id = 123

    user = User(id=user_id)
    assert isinstance(user.id, int)
    assert user.id == user_id
