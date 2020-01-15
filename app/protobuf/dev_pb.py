import typing

import protox

import app.protobuf.imported_pb as \
    imported_pb


class Debug(protox.Message):
    hello_enum: typing.List[imported_pb.ImportedMessage.Hello]

    def __init__(
        self,
        *,
        hello_enum: typing.List[imported_pb.ImportedMessage.Hello] = None,
    ):
        super().__init__(
            hello_enum=hello_enum,
        )


protox.define_fields(
    Debug,
    hello_enum=protox.Repeated(
        number=1, of_type=imported_pb.ImportedMessage.Hello
    ),
)
