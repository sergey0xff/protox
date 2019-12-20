from enum import IntEnum

import protox


class User(protox.Message):
    class Type(IntEnum):
        MERE_MORTAL = 1
        ADMIN = 2

    id: int
    name: str
    type: 'User.Type'

    def __init__(
        self,
        *,
        id: int,
        name: str,
        type: 'User.Type',
    ):
        super().__init__(
            id=id,
            name=name,
            type=type,
        )


protox.define_fields(
    User,
    id=protox.UInt32(
        number=1, required=True
    ),
    name=protox.String(
        number=2, required=True
    ),
    type=protox.EnumField(
        number=3, py_enum=User.Type, default=User.Type.MERE_MORTAL, required=True
    ),
)
