from typing import Dict

from protox import FileDescriptorProto, ServiceDescriptorProto, MethodDescriptorProto
from protox.plugin.common import GRPCLIB_FILE_POSTFIX, to_snake_case, PROTOBUF_FILE_POSTFIX, StringBuffer, \
    is_well_known_type_field
from protox.plugin.index import Index
from protox.plugin.protobuf_code_generator import ProtobufCodeGenerator
from protox.well_known_types.plugin import CodeGeneratorResponse


class GrpclibCodeGenerator:
    server_cardinality_map = {
        True: 'STREAM',
        False: 'UNARY',
    }

    client_cardinality_map = {
        True: 'Stream',
        False: 'Unary',
    }

    def __init__(
        self,
        code_generator: ProtobufCodeGenerator,
    ):
        self._code_gen: ProtobufCodeGenerator = code_generator
        self._index: Index = code_generator.index

    def grpclib_imports(self, import_requests: Dict[str, FileDescriptorProto]) -> str:
        buffer = StringBuffer()

        buffer.write('import abc')
        buffer.write('import typing')
        buffer.nl()

        if 'protox' in import_requests:
            import_requests.pop('protox')
            buffer.write('import protox')

        buffer.write('import grpclib.client')
        buffer.write('import grpclib.const')
        buffer.write('import grpclib.server')
        buffer.nl()

        for file in import_requests.values():
            if self._index.base_package:
                import_path = (
                    self._index.base_package.replace('/', '.') +
                    '.' +
                    self._code_gen.file_to_import_name(file)
                )
            else:
                import_path = self._code_gen.file_to_import_name(file)

            buffer.write(f'import {import_path + PROTOBUF_FILE_POSTFIX} as \\')

            with buffer.indent():
                buffer.write(self._code_gen.file_to_package_name(file) + PROTOBUF_FILE_POSTFIX)

        buffer.nl(2)
        return buffer.read()

    def grpc_type_to_py_name(
        self,
        grpc_type: str,
        import_requests: Dict[str, FileDescriptorProto]
    ) -> str:
        file = self._index.proto_files[grpc_type]

        if is_well_known_type_field(grpc_type):
            import_requests['protox'] = file
            return self._code_gen.resolve_google_protobuf_import(grpc_type)

        import_requests[file.name] = file

        return (
            self._code_gen.file_to_package_name(file) +
            PROTOBUF_FILE_POSTFIX +
            '.' +
            grpc_type.split('.')[-1]
        )

    def grpc_url(
        self,
        service_name: str,
        method_name: str,
    ) -> str:
        if self._code_gen.proto_file.package:
            service_name = f'{self._code_gen.proto_file.package}.{service_name}'

        return f'/{service_name}/{method_name}'

    def write_server_method(
        self,
        service: ServiceDescriptorProto,
        method: MethodDescriptorProto,
        buffer: StringBuffer,
        import_requests: Dict[str, FileDescriptorProto],
    ):
        w = buffer.write

        w(
            f"'{self.grpc_url(service.name, method.name)}'"
            f": grpclib.const.Handler("
        )

        with buffer.indent():
            w(f'self.{to_snake_case(method.name)},')
            w(
                'grpclib.const.Cardinality.',
                self.server_cardinality_map[method.client_streaming],
                '_',
                self.server_cardinality_map[method.server_streaming],
                ',',
            )
            input_message = self.grpc_type_to_py_name(
                method.input_type,
                import_requests,
            )
            w(f'{input_message},')

            output_message = self.grpc_type_to_py_name(
                method.output_type,
                import_requests,
            )
            w(f'{output_message},')

        w('),')

    def write_client_method(
        self,
        service: ServiceDescriptorProto,
        method: MethodDescriptorProto,
        buffer: StringBuffer,
        import_requests: Dict[str, FileDescriptorProto],
    ):
        w = buffer.write

        w(
            'self.',
            to_snake_case(method.name),
            ' = grpclib.client.',
            self.client_cardinality_map[method.client_streaming],
            self.client_cardinality_map[method.server_streaming],
            'Method(',
        )
        input_message = self.grpc_type_to_py_name(
            method.input_type,
            import_requests,
        )
        output_message = self.grpc_type_to_py_name(
            method.output_type,
            import_requests,
        )

        with buffer.indent():
            w('channel,'),
            w("'", self.grpc_url(service.name, method.name), "'", ',')
            w(input_message, ',')
            w(output_message, ',')

        w(')')

    def write_grpclib_service(
        self,
        service: ServiceDescriptorProto,
        buffer: StringBuffer,
    ) -> Dict[str, FileDescriptorProto]:
        import_requests = {}
        w = buffer.write

        w(f'class {service.name}Base(abc.ABC):')

        with buffer.indent():
            if service.method:
                for method in service.method:
                    w('@abc.abstractmethod')
                    w(f'async def {to_snake_case(method.name)}(self, stream: grpclib.server.Stream):')

                    with buffer.indent():
                        w('pass')

                    buffer.nl()

                w('def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:')

                with buffer.indent():
                    w('return {')

                    with buffer.indent():
                        for method in service.method:
                            self.write_server_method(
                                service,
                                method,
                                buffer,
                                import_requests,
                            )

                    w('}')
            else:
                w('def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:')
                with buffer.indent():
                    w('return {}')

        buffer.nl(2)

        w(f'class {service.name}Stub:')
        with buffer.indent():
            if service.method:
                w('def __init__(self, channel: grpclib.client.Channel):')

                with buffer.indent():
                    for method in service.method:
                        self.write_client_method(
                            service,
                            method,
                            buffer,
                            import_requests,
                        )
            else:
                w('pass')

        return import_requests

    def generate(self) -> CodeGeneratorResponse.File:
        buffer = StringBuffer()
        import_requests = {}

        for service in self._code_gen.proto_file.service:
            service_imports = self.write_grpclib_service(
                service,
                buffer,
            )
            import_requests.update(service_imports)

        return CodeGeneratorResponse.File(
            name=self._code_gen.get_file_name(GRPCLIB_FILE_POSTFIX),
            content=(
                self._code_gen.preamble +
                '\n' +
                self.grpclib_imports(import_requests) +
                buffer.read()
            ),
        )
