import typing
from enum import IntEnum

import protox


class User(protox.Message):
    class Type(IntEnum):
        UNDEFINED = 0
        MERE_MORTAL = 1
        ADMIN = 2

    id: int
    name: str
    type: 'User.Type'
    props: typing.Dict[str, 'User.Type']
    ok: typing.Optional[int]
    fail: typing.Optional[int]

    result = protox.one_of(
        'ok',
        'fail',
    )

    def __init__(
        self,
        *,
        id: int = None,
        name: str = None,
        type: 'User.Type' = None,
        props: typing.Dict[str, 'User.Type'] = None,
        ok: typing.Optional[int] = None,
        fail: typing.Optional[int] = None,
    ):
        super().__init__(
            id=id,
            name=name,
            type=type,
            props=props,
            ok=ok,
            fail=fail,
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
    props=protox.MapField(
        number=4, key=protox.String, value=User.Type
    ),
    ok=protox.Int32(
        number=10, required=False
    ),
    fail=protox.Int32(
        number=11, required=False
    ),
)
