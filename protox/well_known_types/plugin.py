from typing import List

from protox import Message, fields
from protox.well_known_types.descriptor import FileDescriptorProto


class Version(Message):
    major: int = fields.Int32(number=1)
    minor: int = fields.Int32(number=2)
    patch: int = fields.Int32(number=3)
    suffix: str = fields.String(number=4)


class CodeGeneratorRequest(Message):
    file_to_generate: List[str] = fields.String.as_repeated(number=1)
    parameter: str = fields.String(number=2)
    proto_file: List[FileDescriptorProto] = FileDescriptorProto.as_repeated(number=15)
    compiler_version: Version = Version.as_field(number=3)


class CodeGeneratorResponse(Message):
    class File(Message):
        name: str = fields.String(number=1)
        insertion_point: str = fields.String(number=2)
        content: str = fields.String(number=15)

    error: str = fields.String(number=1)
    file: List[File] = File.as_repeated(number=15)
