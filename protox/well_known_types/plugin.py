import typing

import protox
from protox.well_known_types import FileDescriptorProto


class Version(protox.Message):
    major: typing.Optional[int]
    minor: typing.Optional[int]
    patch: typing.Optional[int]
    suffix: typing.Optional[str]

    def __init__(
        self,
        *,
        major: typing.Optional[int] = None,
        minor: typing.Optional[int] = None,
        patch: typing.Optional[int] = None,
        suffix: typing.Optional[str] = None,
    ):
        super().__init__(
            major=major,
            minor=minor,
            patch=patch,
            suffix=suffix,
        )


class CodeGeneratorRequest(protox.Message):
    file_to_generate: typing.List[str]
    parameter: typing.Optional[str]
    proto_file: typing.List[FileDescriptorProto]
    compiler_version: typing.Optional['Version']

    def __init__(
        self,
        *,
        file_to_generate: typing.List[str] = None,
        parameter: typing.Optional[str] = None,
        proto_file: typing.List[FileDescriptorProto] = None,
        compiler_version: typing.Optional['Version'] = None,
    ):
        super().__init__(
            file_to_generate=file_to_generate,
            parameter=parameter,
            proto_file=proto_file,
            compiler_version=compiler_version,
        )


class CodeGeneratorResponse(protox.Message):
    class File(protox.Message):
        name: typing.Optional[str]
        insertion_point: typing.Optional[str]
        content: typing.Optional[str]

        def __init__(
            self,
            *,
            name: typing.Optional[str] = None,
            insertion_point: typing.Optional[str] = None,
            content: typing.Optional[str] = None,
        ):
            super().__init__(
                name=name,
                insertion_point=insertion_point,
                content=content,
            )

    error: typing.Optional[str]
    file: typing.List['CodeGeneratorResponse.File']

    def __init__(
        self,
        *,
        error: typing.Optional[str] = None,
        file: typing.List['CodeGeneratorResponse.File'] = None,
    ):
        super().__init__(
            error=error,
            file=file,
        )


protox.define_fields(
    Version,
    major=protox.Int32(
        number=1, required=False
    ),
    minor=protox.Int32(
        number=2, required=False
    ),
    patch=protox.Int32(
        number=3, required=False
    ),
    suffix=protox.String(
        number=4, required=False
    ),
)

protox.define_fields(
    CodeGeneratorRequest,
    file_to_generate=protox.String.as_repeated(
        number=1
    ),
    parameter=protox.String(
        number=2, required=False
    ),
    proto_file=FileDescriptorProto.as_repeated(
        number=15
    ),
    compiler_version=Version.as_field(
        number=3
    ),
)

protox.define_fields(
    CodeGeneratorResponse,
    error=protox.String(
        number=1, required=False
    ),
    file=CodeGeneratorResponse.File.as_repeated(
        number=15
    ),
)

protox.define_fields(
    CodeGeneratorResponse.File,
    name=protox.String(
        number=1, required=False
    ),
    insertion_point=protox.String(
        number=2, required=False
    ),
    content=protox.String(
        number=15, required=False
    ),
)
