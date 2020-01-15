import typing

import protox

import app.protobuf.imported_pb as \
    imported_pb
import app.protobuf.imported_enum_pb as \
    imported_enum_pb


class Debug(protox.Message):
    hello_enum: typing.Optional[imported_pb.ImportedMessage.Hello]
    color: typing.Optional[imported_enum_pb.Hello.Color]

    def __init__(
        self,
        *,
        hello_enum: typing.Optional[imported_pb.ImportedMessage.Hello] = None,
        color: typing.Optional[imported_enum_pb.Hello.Color] = None,
    ):
        super().__init__(
            hello_enum=hello_enum,
            color=color,
        )


protox.define_fields(
    Debug,
    hello_enum=protox.EnumField(
        number=1, py_enum=imported_pb.ImportedMessage.Hello, required=False
    ),
    color=protox.EnumField(
        number=2, py_enum=imported_enum_pb.Hello.Color, required=False
    ),
)
