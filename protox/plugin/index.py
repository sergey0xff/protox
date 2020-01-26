from typing import Dict

from protox import DescriptorProto, FileDescriptorProto
from protox.well_known_types.plugin import CodeGeneratorRequest


class Index:
    def __init__(
        self,
        request: CodeGeneratorRequest,
        base_package: str,
    ):
        self._request: CodeGeneratorRequest = request
        self._base_package: str = base_package
        # maps message names to message descriptors
        self._messages: Dict[str, DescriptorProto] = {}
        # maps protobuf file names to protobuf file descriptors
        self._proto_files: Dict[str, FileDescriptorProto] = {}

        self._build()

    @property
    def request(self) -> CodeGeneratorRequest:
        return self._request

    @property
    def base_package(self) -> str:
        return self._base_package

    @property
    def messages(self) -> Dict[str, DescriptorProto]:
        return self._messages

    @property
    def proto_files(self) -> Dict[str, FileDescriptorProto]:
        return self._proto_files

    def _build(self):
        for proto_file in self._request.proto_file:
            self._visit_proto_file(proto_file)

    def _visit_proto_file(self, proto_file):
        if proto_file.package:
            prefix = '.' + proto_file.package + '.'
        else:
            prefix = '.'

        for message in proto_file.message_type:
            self._visit_message(
                prefix,
                message,
                proto_file,
            )

        for enum in proto_file.enum_type:
            self._visit_enum(
                prefix,
                enum,
                proto_file,
            )

    def _visit_message(
        self,
        prefix: str,
        message: DescriptorProto,
        proto_file: FileDescriptorProto,
    ):
        full_message_name = prefix + message.name
        self._proto_files[full_message_name] = proto_file
        self._messages[full_message_name] = message

        for nested_type in message.nested_type:
            self._visit_message(
                full_message_name + '.',
                nested_type,
                proto_file,
            )

        for enum_type in message.enum_type:
            self._visit_enum(
                full_message_name + '.',
                enum_type,
                proto_file,
            )

    def _visit_enum(self, prefix, enum, proto_file):
        self._proto_files[prefix + enum.name] = proto_file
