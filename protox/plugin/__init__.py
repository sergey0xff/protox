#!/usr/bin/env python3
import argparse
import re
import shlex
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Set, Tuple

# FIXME: delete before releasing the library
sys.path.append(
    str(Path(__file__).parent.parent.parent)
)
from protox import FieldDescriptorProto, DescriptorProto, FileDescriptorProto, EnumDescriptorProto, \
    ServiceDescriptorProto
from protox.well_known_types.plugin import CodeGeneratorRequest, CodeGeneratorResponse

reserved_names = [
    'False',
    'None',
    'True',
    'and',
    'as',
    'assert',
    'async',
    'await',
    'break',
    'class',
    'continue',
    'def',
    'del',
    'elif',
    'else',
    'except',
    'finally',
    'for',
    'from',
    'global',
    'if',
    'import',
    'in',
    'is',
    'lambda',
    'nonlocal',
    'not',
    'or',
    'pass',
    'raise',
    'return',
    'try',
    'while',
    'with',
    'yield',

    # types,
    'protox',
    'grpclib',
    'int',
    'float',
    'bool',
    'str',
    'bytes',
    'typing',
    'abc',

    # FIXME: `enum` probably not used
    'enum',
    'IntEnum',
]

protobuf_file_postfix = '_pb'
grpclib_file_postfix = '_grpclib'


def pythonize_name(name: str) -> str:
    if name in reserved_names:
        return name + '_'

    return name


def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def is_empty_message(message: DescriptorProto) -> bool:
    return (
        not message.nested_type and
        not message.field and
        not message.enum_type
    )


def collect_one_of(message: DescriptorProto) -> Dict[str, List[str]]:
    one_ofs = {}
    one_of_by_index = []

    for one_of in message.oneof_decl:
        lst = []
        one_ofs[one_of.name] = lst
        one_of_by_index.append(lst)

    for field in message.field:
        if field.has_field('oneof_index'):
            one_of_by_index[field.oneof_index].append(field.name)

    return one_ofs


def pb_to_py_type(pb_type: FieldDescriptorProto.Type) -> str:
    fd = FieldDescriptorProto.Type

    return {
        fd.TYPE_DOUBLE: 'float',
        fd.TYPE_FLOAT: 'float',

        fd.TYPE_INT64: 'int',
        fd.TYPE_UINT64: 'int',
        fd.TYPE_INT32: 'int',
        fd.TYPE_UINT32: 'int',
        fd.TYPE_FIXED64: 'int',
        fd.TYPE_FIXED32: 'int',
        fd.TYPE_SFIXED32: 'int',
        fd.TYPE_SFIXED64: 'int',
        fd.TYPE_SINT32: 'int',
        fd.TYPE_SINT64: 'int',

        fd.TYPE_STRING: 'str',
        fd.TYPE_BYTES: 'bytes',

        fd.TYPE_BOOL: 'bool',
        fd.TYPE_ENUM: 'enum.IntEnum',
    }[pb_type]


def pb_to_protox_type(pb_type: FieldDescriptorProto.Type) -> str:
    fd = FieldDescriptorProto.Type

    return {
        fd.TYPE_DOUBLE: 'Double',
        fd.TYPE_FLOAT: 'Float',

        fd.TYPE_INT64: 'Int64',
        fd.TYPE_UINT64: 'UInt64',
        fd.TYPE_INT32: 'Int32',
        fd.TYPE_UINT32: 'UInt32',
        fd.TYPE_FIXED64: 'Fixed64',
        fd.TYPE_FIXED32: 'Fixed32',
        fd.TYPE_SFIXED32: 'SFixed32',
        fd.TYPE_SFIXED64: 'SFixed64',
        fd.TYPE_SINT32: 'SInt32',
        fd.TYPE_SINT64: 'SInt64',

        fd.TYPE_STRING: 'String',
        fd.TYPE_BYTES: 'Bytes',

        fd.TYPE_BOOL: 'Bool',
        fd.TYPE_ENUM: 'EnumField',
    }[pb_type]


def pythonize_default_value(default_value: str) -> str:
    return {
        'true': 'True',
        'false': 'False',
    }.get(default_value, default_value)


def debug(*args):
    sys.stderr.write(''.join(map(str, args)) + '\n')


def parse_base_package(parameter: str) -> str:
    parts = parameter.split(',')

    for part in parts:
        part = part.strip()

        if part.startswith('base_package'):
            try:
                _, value = part.split('=')
            except ValueError:
                raise Exception(
                    f'Could not parse option: {part}'
                )

            return value.strip()

    return ''


class Index:
    def __init__(
        self,
        request: CodeGeneratorRequest,
        base_package: str,
    ):
        self.request = request
        self.base_package = base_package
        # messages by full names
        self.messages: dict = {}
        # protobuf file descriptors by full names
        self.proto_files: dict = {}
        self._build()

    def _build(self):
        for proto_file in self.request.proto_file:
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

    def _visit_message(self, prefix, message, proto_file):
        full_name = prefix + message.name
        self.proto_files[full_name] = proto_file
        self.messages[full_name] = message

        for nested_type in message.nested_type:
            self._visit_message(
                full_name + '.',
                nested_type,
                proto_file,
            )

    def _visit_enum(self, prefix, enum, proto_file):
        self.proto_files[prefix + enum.name] = proto_file


class StringBuffer:
    def __init__(self):
        self._buffer = []
        self._indent = 0

    @contextmanager
    def indent(self):
        self._indent += 1
        yield
        self._indent -= 1

    def write(self, *args: str):
        self._buffer.append(' ' * 4 * self._indent)

        for x in args:
            self._buffer.append(x)

        self._buffer.append('\n')

    def nl(self, n=1):
        self._buffer.append('\n' * n)

    def read(self) -> str:
        return ''.join(self._buffer)


def is_optional(field: FieldDescriptorProto) -> bool:
    return field.label == FieldDescriptorProto.Label.LABEL_OPTIONAL


def is_required(field: FieldDescriptorProto) -> bool:
    return field.label == FieldDescriptorProto.Label.LABEL_REQUIRED


def is_repeated(field: FieldDescriptorProto) -> bool:
    return field.label == FieldDescriptorProto.Label.LABEL_REPEATED


def is_message_field(field: FieldDescriptorProto) -> bool:
    return field.type == FieldDescriptorProto.Type.TYPE_MESSAGE


def is_enum_field(field: FieldDescriptorProto) -> bool:
    return field.type == FieldDescriptorProto.Type.TYPE_ENUM


def is_group_field(field: FieldDescriptorProto) -> bool:
    return field.type == FieldDescriptorProto.Type.TYPE_GROUP


def is_well_known_type_field(type_name: str) -> bool:
    return type_name.startswith('.google.protobuf')


class FieldMangler:
    def __init__(self, message: DescriptorProto, snake_case_flag: bool):
        # original field names
        self._message_fields = set(
            x.name for x in message.field
        )
        self._name_counter = Counter()
        self._snake_case_flag = snake_case_flag

        # maps original field names to mangled ones
        self._mangled_names: Dict[str, str] = {}

        for name in self._message_fields:
            self._process_name(name)

    def _mangle_name(self, name: str) -> str:
        self._name_counter[name] += 1

        while f'{name}_{self._name_counter[name]}' in self._message_fields:
            self._name_counter[name] += 1

        return f'{name}_{self._name_counter[name]}'

    def _process_name(self, name: str):
        if self._snake_case_flag:
            py_name = to_snake_case(name)
        else:
            py_name = name

        if (
            py_name in reserved_names
            or
            py_name != name and py_name in self._message_fields
        ):
            py_name = self._mangle_name(py_name)

        self._mangled_names[name] = py_name

    def get(self, field: str) -> str:
        if field not in self._message_fields:
            raise ValueError('No such name')

        return self._mangled_names[field]


class CodeGenerator:
    def __init__(self, proto_file: FileDescriptorProto, index: Index, args):
        self._proto_file: FileDescriptorProto = proto_file
        self._index: Index = index
        self._args = args
        self._indent = 0
        self._uses_enums = False
        self._uses_typing = False
        self._import_requests = {}
        self._buffer = StringBuffer()
        self._import_buffer = StringBuffer()
        self._field_manglers = {}

    def empty(self) -> bool:
        return not (
            self._proto_file.enum_type or
            self._proto_file.message_type
        )

    def has_services(self) -> bool:
        return bool(self._proto_file.service)

    def resolve_field_name(self, message: DescriptorProto, field: str) -> str:
        if message.name not in self._field_manglers:
            self._field_manglers[message.name] = FieldMangler(
                message,
                self._args.snake_case
            )

        return self._field_manglers[message.name].get(field)

    def is_local_type(self, py_type: str):
        """
        Checks if py_type defined in current file
        """
        return (
            not py_type
            or
            self._index.proto_files.get(py_type) == self._proto_file
        )

    @staticmethod
    def file_to_import_name(file: FileDescriptorProto) -> str:
        return (
            file.name
                .replace('.proto', '')
                .replace('-', '_')
                .replace('/', '.')
        )

    @staticmethod
    def file_to_package_name(file: FileDescriptorProto) -> str:
        return (
            file.name
                .replace('.proto', '')
                .replace('-', '_')
                .replace('/', '__')
        )

    @staticmethod
    def resolve_google_protobuf_import(type_name: str) -> str:
        type_name = type_name.split(".")[-1]
        return f'protox.{type_name}'

    def resolve_field_import(self, field: FieldDescriptorProto) -> str:
        """
        Requests import of the file in which the imported message is
        """
        if is_well_known_type_field(field.type_name):
            return self.resolve_google_protobuf_import(field.type_name)

        field_type = field.type_name

        if is_enum_field(field):
            enum_field_type = '.'.join(field_type.split('.')[:-1])
        else:
            enum_field_type = None

        try:
            file = self._index.proto_files[enum_field_type]
        except KeyError:
            file = self._index.proto_files[field_type]

        package = self.file_to_package_name(file)
        self._import_requests[file.name] = file
        imported_name = (
            package +
            protobuf_file_postfix.rstrip('.') +
            '.' +
            field_type[1 + len(file.package or ''):].lstrip('.')
        )

        return imported_name

    def is_map_field(self, field: FieldDescriptorProto) -> bool:
        if not is_message_field(field):
            return False

        if not is_repeated(field):
            return False

        return self.is_map_message(
            self._index.messages[field.type_name]
        )

    def is_map_message(self, message: DescriptorProto) -> bool:
        try:
            return bool(message.options.map_entry)
        except AttributeError:
            return False

    def map_message_py_types(self, message: DescriptorProto) -> Tuple[str, str]:
        key_type = self.resolve_field_type(message.field[0])
        value_type = self.resolve_field_type(message.field[1])
        return key_type, value_type

    def map_message_protox_types(self, message: DescriptorProto) -> Tuple[str, str]:
        if is_message_field(message.field[0]):
            key_type = self.resolve_field_import(message.field[0])
        else:
            key_type = 'protox.' + pb_to_protox_type(message.field[0].type)

        if is_message_field(message.field[1]):
            value_type = self.resolve_field_import(message.field[1])
        elif is_enum_field(message.field[1]):
            field = message.field[1]
            path = '.'.join(field.type_name.split('.')[:-1])

            if self.is_local_type(path):
                value_type = field.type_name.lstrip('.')
            else:
                value_type = self.resolve_field_import(field)
        else:
            value_type = 'protox.' + pb_to_protox_type(message.field[1].type)

        return key_type, value_type

    def resolve_field_type(self, field: FieldDescriptorProto) -> str:
        if self.is_map_field(field):
            message = self._index.messages[field.type_name]
            key_type, value_type = self.map_message_py_types(message)
            py_type = f'typing.Dict[{key_type}, {value_type}]'
            self._uses_typing = True
        elif is_message_field(field):
            if self.is_local_type(field.type_name):
                py_type = f"'{field.type_name.lstrip('.')}'"
            else:
                py_type = self.resolve_field_import(field)
        elif is_enum_field(field):
            path = '.'.join(field.type_name.split('.')[:-1])

            if self.is_local_type(path):
                field_type = field.type_name.lstrip('.')
                field_type = field_type[len(self._proto_file.package):]
                field_type = field_type.lstrip('.')
                py_type = f"'{field_type}'"
            else:
                py_type = self.resolve_field_import(field)
        elif is_group_field(field):
            raise NotImplementedError(
                'Groups are not supported yet'
            )
        else:
            py_type = pb_to_py_type(field.type)

        return py_type

    def apply_field_label(self, field: FieldDescriptorProto, py_type: str) -> str:
        if self.is_map_field(field):
            self._uses_typing = True
        elif is_optional(field):
            py_type = f'typing.Optional[{py_type}]'
            self._uses_typing = True
        elif is_repeated(field):
            py_type = f'typing.List[{py_type}]'
            self._uses_typing = True

        return py_type

    def write_message(self, message: DescriptorProto):
        w = self._buffer.write
        nl = self._buffer.nl
        indent = self._buffer.indent

        w(f'class {message.name}(protox.Message):')

        if is_empty_message(message):
            with indent():
                w('pass')
            return

        # body
        with indent():
            # enums
            for enum_type in message.enum_type:
                self.write_enum(enum_type)
                nl()

            # nested messages
            for nested_type in message.nested_type:
                if not self.is_map_message(nested_type):
                    self.write_message(nested_type)
                    nl()

            if not message.field:
                return

            # fields
            for field in message.field:
                py_type = self.apply_field_label(
                    field,
                    self.resolve_field_type(field)
                )
                w(f'{self.resolve_field_name(message, field.name)}: {py_type}')

            nl()

            if self.write_oneofs(message):
                nl()

            self.write_init(message)

    def write_init(self, message: DescriptorProto):
        w = self._buffer.write
        indent = self._buffer.indent

        w('def __init__(')

        with indent():
            w('self,')
            w('*,')
            for field in message.field:
                py_type = self.apply_field_label(
                    field,
                    self.resolve_field_type(field)
                )

                w(f'{self.resolve_field_name(message, field.name)}: {py_type} = None,')

        w('):')

        with indent():
            w('super().__init__(')

            with indent():
                for field in message.field:
                    field_name = self.resolve_field_name(message, field.name)
                    w(f'{field_name}={field_name},')

            w(')')

    def write_oneofs(self, message: DescriptorProto):
        w = self._buffer.write
        one_ofs = collect_one_of(message).items()

        for name, fields in one_ofs:
            w(f'{name} = protox.one_of(')

            with self._buffer.indent():
                for field in fields:
                    w(f"'{field}',")

            w(')')

        return bool(one_ofs)

    def write_enum(self, enum_type: EnumDescriptorProto):
        self._uses_enums = True

        self._buffer.write(f'class {enum_type.name}(IntEnum):')

        with self._buffer.indent():
            for field in enum_type.value:
                self._buffer.write(f'{field.name} = {field.number}')

    def write_imports(self):
        w = self._import_buffer.write
        nl = self._import_buffer.nl

        if self._uses_typing:
            w('import typing')

        if self._uses_enums:
            w('from enum import IntEnum')

        if self._uses_enums or self._uses_typing:
            nl()

        w('import protox\n')

        for file in self._import_requests.values():
            if self._index.base_package:
                import_path = self._index.base_package.replace('/', '.') + '.' + self.file_to_import_name(file)
            else:
                import_path = self.file_to_import_name(file)

            w(f'import {import_path + protobuf_file_postfix} as \\')

            with self._import_buffer.indent():
                w(self.file_to_package_name(file) + protobuf_file_postfix)

        if self._import_requests:
            nl()

        nl()

    def write_define_fields(self, message: DescriptorProto, path: str = ''):
        w = self._buffer.write

        if not message.field:
            return

        w('protox.define_fields(')

        with self._buffer.indent():
            w(f'{path}{message.name},')
            for field in message.field:
                field_kwargs = {
                    'number': field.number
                }

                if self.is_map_field(field):
                    field_type = 'protox.MapField'
                    key_type, value_type = self.map_message_protox_types(
                        self._index.messages[field.type_name]
                    )
                    field_kwargs['key'] = key_type
                    field_kwargs['value'] = value_type
                elif is_message_field(field):
                    field_type = self.resolve_field_type(field).strip("'")
                    field_type = f'{field_type}.as_field'
                elif is_enum_field(field):
                    field_type = 'protox.EnumField'
                    py_enum = self.resolve_field_type(field).strip("'")

                    if is_repeated(field):
                        field_kwargs['of_type'] = py_enum
                    else:
                        field_kwargs['py_enum'] = py_enum

                    if field.default_value:
                        field_kwargs['default'] = py_enum + '.' + field.default_value
                elif is_group_field(field):
                    raise NotImplementedError(
                        'Groups are not supported yet'
                    )
                else:
                    field_type = f'protox.{pb_to_protox_type(field.type)}'

                    if field.default_value:
                        field_kwargs['default'] = pythonize_default_value(field.default_value)

                if self.is_map_field(field):
                    pass
                elif is_repeated(field):
                    if field.options and field.options.packed:
                        field_kwargs['packed'] = True

                    field_type = field_type.replace('.as_field', '')

                    if is_enum_field(field):
                        field_type = f'protox.Repeated'
                    else:
                        field_type = f'{field_type}.as_repeated'
                elif is_optional(field):
                    field_kwargs['required'] = 'False'
                else:
                    field_kwargs['required'] = 'True'

                w(f'{self.resolve_field_name(message, field.name)}={field_type}(')

                with self._buffer.indent():
                    w(', '.join(
                        [
                            f'{key}={value}'
                            for key, value in field_kwargs.items()
                        ]
                    ))

                w('),')

        w(')\n')

        for nested_type in message.nested_type:
            self.write_define_fields(nested_type, path=message.name + '.')

    def generate(self) -> CodeGeneratorResponse.File:
        nl = self._buffer.nl

        # enums
        for enum_type in self._proto_file.enum_type:
            self.write_enum(enum_type)
            nl(2)

        # messages
        for message_type in self._proto_file.message_type:
            self.write_message(message_type)
            nl(2)

        # message fields
        for message_type in self._proto_file.message_type:
            self.write_define_fields(message_type)

        self.write_imports()
        imports = self._import_buffer.read()
        content = self._buffer.read().strip('\n') + '\n'

        return CodeGeneratorResponse.File(
            name=self.get_file_name(protobuf_file_postfix),
            content=(
                imports +
                content
            ),
        )

    def get_file_name(self, postfix: str) -> str:
        filename = (
            self._proto_file.name.strip().replace('.proto', '') +
            f'{postfix}.py'
        )

        if self._index.base_package:
            filename = self._index.base_package + '/' + filename

        return filename

    def grpclib_imports(self, import_requests: dict) -> str:
        buffer = StringBuffer()

        buffer.write('import abc')
        buffer.write('import typing')
        buffer.nl()

        buffer.write('import grpclib.const')
        buffer.write('import grpclib.client')
        buffer.write('import grpclib.server')
        buffer.nl()

        for file in import_requests.values():
            if self._index.base_package:
                import_path = self._index.base_package.replace('/', '.') + '.' + self.file_to_import_name(file)
            else:
                import_path = self.file_to_import_name(file)

            buffer.write(f'import {import_path + protobuf_file_postfix} as \\')

            with buffer.indent():
                buffer.write(self.file_to_package_name(file) + protobuf_file_postfix)

        buffer.nl(2)
        return buffer.read()

    def generate_grpclib_services(self) -> CodeGeneratorResponse.File:
        buffer = StringBuffer()
        import_requests = {}

        for service in self._proto_file.service:
            service_imports = self.write_grpclib_service(
                service,
                buffer,
            )
            import_requests.update(service_imports)

        return CodeGeneratorResponse.File(
            name=self.get_file_name(grpclib_file_postfix),
            content=self.grpclib_imports(import_requests) + buffer.read(),
        )

    def grpc_type_to_py_name(self, grpc_type: str, import_requests: dict):
        file = self._index.proto_files[grpc_type]
        import_requests[file.name] = file

        return (
            self.file_to_package_name(file) +
            protobuf_file_postfix +
            '.' +
            grpc_type.split('.')[-1]
        )

    def grpc_url(self, service_name: str, method_name: str):
        return f'/{self._proto_file.package}.{service_name}/{method_name}'

    def write_grpclib_service(
        self,
        service: ServiceDescriptorProto,
        buffer: StringBuffer,
    ) -> dict:
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
                            w(f"'{self.grpc_url(service.name, method.name)}': grpclib.const.Handler(")

                            with buffer.indent():
                                cardinality_map = {
                                    False: 'UNARY',
                                    True: 'STREAM'
                                }

                                buffer.write(f'self.{to_snake_case(method.name)},')
                                buffer.write(
                                    'grpclib.const.Cardinality.',
                                    cardinality_map[method.client_streaming],
                                    '_',
                                    cardinality_map[method.server_streaming],
                                    ',',
                                )
                                input_message = self.grpc_type_to_py_name(
                                    method.input_type,
                                    import_requests,
                                )
                                output_message = self.grpc_type_to_py_name(
                                    method.output_type,
                                    import_requests,
                                )

                                buffer.write(f'{input_message},')
                                buffer.write(f'{output_message},')

                            w('),')

                    w('}')
            else:
                w('def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:')
                with buffer.indent():
                    w('return {}')

        buffer.nl(2)

        w(f'class {service.name}Stub:')
        with buffer.indent():
            cardinality_map = {
                False: 'Unary',
                True: 'Stream'
            }

            if service.method:
                w('def __init__(self, channel: grpclib.client.Channel):')

                with buffer.indent():
                    for method in service.method:
                        w(
                            'self.',
                            to_snake_case(method.name),
                            ' = grpclib.client.',
                            cardinality_map[method.client_streaming],
                            cardinality_map[method.server_streaming],
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
            else:
                w('pass')

        return import_requests


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Protox cli'
    )

    parser.add_argument(
        '--base-package-dir',
        default='',
        type=str,
        help='Base python package directory relative to the root directory. E.g. app/protobuf, .'
    )
    parser.add_argument(
        '--with-dependencies',
        action='store_true',
        help='If enabled all imported .proto files are also generated',
    )
    parser.add_argument(
        '--snake-case',
        action='store_true',
        help='If enabled message fields, enum variants and grpc methods are renamed to snake_case'
    )
    parser.add_argument(
        '--grpclib',
        action='store_true',
        help='If enabled grpclib services are generated'
    )

    return parser


def main():
    # data = b'\n\x14simple_service.proto\x12)--base-package-dir=app/protobuf --grpclib\x1a\x08\x08\x03\x10\x06\x18\x01"\x00z\x81\x06\n\x14simple_service.proto\x12\x12services.ping_pong"\t\n\x07Request"\n\n\x08Response2\xba\x02\n\x08PingPong\x12G\n\nUnaryUnary\x12\x1b.services.ping_pong.Request\x1a\x1c.services.ping_pong.Response\x12J\n\x0bUnaryStream\x12\x1b.services.ping_pong.Request\x1a\x1c.services.ping_pong.Response0\x01\x12J\n\x0bStreamUnary\x12\x1b.services.ping_pong.Request\x1a\x1c.services.ping_pong.Response(\x01\x12M\n\x0cStreamStream\x12\x1b.services.ping_pong.Request\x1a\x1c.services.ping_pong.Response(\x010\x01J\xf8\x02\n\x06\x12\x04\x00\x00\x0f\x01\n\x08\n\x01\x0c\x12\x03\x00\x00\x12\n\x08\n\x01\x02\x12\x03\x02\x08\x1a\n\n\n\x02\x04\x00\x12\x04\x04\x00\x05\x01\n\n\n\x03\x04\x00\x01\x12\x03\x04\x08\x0f\n\n\n\x02\x04\x01\x12\x04\x07\x00\x08\x01\n\n\n\x03\x04\x01\x01\x12\x03\x07\x08\x10\n\n\n\x02\x06\x00\x12\x04\n\x00\x0f\x01\n\n\n\x03\x06\x00\x01\x12\x03\n\x08\x10\n\x0b\n\x04\x06\x00\x02\x00\x12\x03\x0b\x040\n\x0c\n\x05\x06\x00\x02\x00\x01\x12\x03\x0b\x08\x12\n\x0c\n\x05\x06\x00\x02\x00\x02\x12\x03\x0b\x14\x1b\n\x0c\n\x05\x06\x00\x02\x00\x03\x12\x03\x0b&.\n\x0b\n\x04\x06\x00\x02\x01\x12\x03\x0c\x048\n\x0c\n\x05\x06\x00\x02\x01\x01\x12\x03\x0c\x08\x13\n\x0c\n\x05\x06\x00\x02\x01\x02\x12\x03\x0c\x15\x1c\n\x0c\n\x05\x06\x00\x02\x01\x06\x12\x03\x0c\'-\n\x0c\n\x05\x06\x00\x02\x01\x03\x12\x03\x0c.6\n\x0b\n\x04\x06\x00\x02\x02\x12\x03\r\x048\n\x0c\n\x05\x06\x00\x02\x02\x01\x12\x03\r\x08\x13\n\x0c\n\x05\x06\x00\x02\x02\x05\x12\x03\r\x15\x1b\n\x0c\n\x05\x06\x00\x02\x02\x02\x12\x03\r\x1c#\n\x0c\n\x05\x06\x00\x02\x02\x03\x12\x03\r.6\n\x0b\n\x04\x06\x00\x02\x03\x12\x03\x0e\x04@\n\x0c\n\x05\x06\x00\x02\x03\x01\x12\x03\x0e\x08\x14\n\x0c\n\x05\x06\x00\x02\x03\x05\x12\x03\x0e\x16\x1c\n\x0c\n\x05\x06\x00\x02\x03\x02\x12\x03\x0e\x1d$\n\x0c\n\x05\x06\x00\x02\x03\x06\x12\x03\x0e/5\n\x0c\n\x05\x06\x00\x02\x03\x03\x12\x03\x0e6>b\x06proto3'
    data = sys.stdin.buffer.read()
    # debug(data)
    # return

    # Parse request
    request = CodeGeneratorRequest.from_bytes(data)

    # args
    parameter = (request.parameter or '').strip('"\'')
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(
        shlex.split(parameter)
    )

    # build index
    index = Index(
        request,
        args.base_package_dir
    )

    # Create response
    files_to_generate: Set[str] = set(request.file_to_generate)

    # filter out google/protobuf files
    files = [
        x for x in request.proto_file
        if not x.name.startswith('google/protobuf/')
    ]

    if not args.with_dependencies:
        files = [
            x for x in request.proto_file
            if x.name in files_to_generate
        ]

    code_generators = [
        CodeGenerator(file, index, args)
        for file in files
    ]

    response_files = [
        x.generate()
        for x in code_generators
        if not x.empty()
    ]

    if args.grpclib:
        response_files += [
            x.generate_grpclib_services()
            for x in code_generators
            if x.has_services()
        ]

    response = CodeGeneratorResponse(
        file=response_files
    )

    sys.stdout.buffer.write(
        response.to_bytes()
    )


if __name__ == '__main__':
    main()
