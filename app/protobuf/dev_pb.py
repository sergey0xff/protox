import typing

import protox

import app.protobuf.service.imported_pb as \
    service__imported_pb


class Debug(protox.Message):
    hello_enum: typing.Optional[service__imported_pb.ImportedMessage.Hello]
    repeated_enum: typing.List[service__imported_pb.ImportedMessage.Hello]

    def __init__(
        self,
        *,
        hello_enum: typing.Optional[service__imported_pb.ImportedMessage.Hello] = None,
        repeated_enum: typing.List[service__imported_pb.ImportedMessage.Hello] = None,
    ):
        super().__init__(
            hello_enum=hello_enum,
            repeated_enum=repeated_enum,
        )


protox.define_fields(
    Debug,
    hello_enum=protox.EnumField(
        number=1, py_enum=service__imported_pb.ImportedMessage.Hello, required=False
    ),
    repeated_enum=protox.Repeated(
        number=2, of_type=service__imported_pb.ImportedMessage.Hello
    ),
)
