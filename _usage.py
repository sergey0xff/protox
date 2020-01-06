from enum import IntEnum

import typing

import protox


class MyMessage(protox.Message):
    class Color(IntEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    map: typing.Dict[str, Color] = protox.MapField(
        key=protox.String,
        value=Color,
        number=1
    )


message = MyMessage()
print(message.map)

message.map['xx'] = MyMessage.Color.BLUE
print(message.to_dict()['map'])