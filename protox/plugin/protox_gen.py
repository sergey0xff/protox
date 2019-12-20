#!/usr/bin/env python3
import sys
from contextlib import contextmanager

from google.protobuf.compiler import plugin_pb2
from google.protobuf.descriptor import FieldDescriptor

reserved_keywords = [
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
    'int',
    'float',
    'bool',
    'enum',
    'str',
    'bytes',
    'typing',
    'IntEnum',
]

protobuf_file_postfix = '_pb'


def pythonize_name(name: str) -> str:
    if name in reserved_keywords:
        return name + '_'

    return name


def is_empty_message(message):
    return (
        not message.nested_type and
        not message.field and
        not message.enum_type
    )


def pb_to_py_type(pb_type):
    fd = FieldDescriptor

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


def pb_to_protox_type(pb_type):
    fd = FieldDescriptor

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
    def __init__(self, request: plugin_pb2.CodeGeneratorRequest):
        self.request = request
        self.base_package = parse_base_package(request.parameter).rstrip('/')
        # messages by full names
        self.messages: dict = {}
        # protobuf file descriptors by full names
        self.proto_files: dict = {}
        self._build()

    def same_file(self, type_a: str, type_b: str) -> bool:
        """
        Checks whether two types defined in the same file
        """
        pass

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


def is_optional(field: FieldDescriptor) -> bool:
    return field.label == FieldDescriptor.LABEL_OPTIONAL


def is_required(field: FieldDescriptor) -> bool:
    return field.label == FieldDescriptor.LABEL_REQUIRED


def is_repeated(field: FieldDescriptor) -> bool:
    return field.label == FieldDescriptor.LABEL_REPEATED


def is_message_field(field: FieldDescriptor) -> bool:
    return field.type == FieldDescriptor.TYPE_MESSAGE


def is_enum_field(field: FieldDescriptor) -> bool:
    return field.type == FieldDescriptor.TYPE_ENUM


def is_group_field(field: FieldDescriptor) -> bool:
    return field.type == FieldDescriptor.TYPE_GROUP


class CodeGenerator:
    def __init__(self, proto_file, index: Index):
        self._proto_file = proto_file
        self._index = index
        self._indent = 0
        self._uses_enums = False
        self._uses_typing = False
        self._import_requests = {}
        self._buffer = StringBuffer()
        self._import_buffer = StringBuffer()

    def is_local_type(self, py_type: str):
        """
        Checks if py_type defined in current file
        """
        return (
            py_type == '' or
            self._index.proto_files[py_type] == self._proto_file
        )

    @staticmethod
    def import_name(file):
        return (
            file.name
                .replace('.proto', '')
                .replace('-', '_')
                .replace('/', '.')
        )

    @staticmethod
    def package_name(file):
        return (
            file.name
                .replace('.proto', '')
                .replace('-', '_')
                .replace('/', '__')
        )

    def resolve_import(self, field):
        """
        Requests import of the file in which the imported message is
        """
        field_type = field.type_name

        if is_enum_field(field):
            field_type = '.'.join(field_type.split('.')[:-1])

        file = self._index.proto_files[field_type]

        package = self.package_name(file)
        self._import_requests[file.name] = file

        return (
            package +
            f'{protobuf_file_postfix}.' +
            field.type_name[2 + len(file.package):]
        )

    def resolve_field_type(self, field):
        if is_message_field(field):
            if self.is_local_type(field.type_name):
                py_type = f"'{field.type_name.lstrip('.')}'"
            else:
                py_type = self.resolve_import(field)
        elif is_enum_field(field):
            path = '.'.join(field.type_name.split('.')[:-1])

            if self.is_local_type(path):
                py_type = f"'{field.type_name.lstrip('.')}'"
            else:
                py_type = self.resolve_import(field)
        elif is_group_field(field):
            raise NotImplementedError(
                'Groups are not supported yet'
            )
        else:
            py_type = pb_to_py_type(field.type)

        return py_type

    def apply_field_label(self, field, py_type):
        if is_optional(field):
            py_type = f'typing.Optional[{py_type}]'
            self._uses_typing = True
        elif is_repeated(field):
            py_type = f'typing.List[{py_type}]'
            self._uses_typing = True

        return py_type

    def write_message(self, message):
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
                w(f'{field.name}: {py_type}')

            nl()
            # init
            w('def __init__(')

            with indent():
                w('self,')
                w('*,')
                for field in message.field:
                    py_type = self.apply_field_label(
                        field,
                        self.resolve_field_type(field)
                    )

                    default_value = ''

                    if is_optional(field):
                        default_value = ' = None'
                    elif is_repeated(field):
                        default_value = ' = tuple()'

                    w(f'{field.name}: {py_type}{default_value},')

            w('):')

            with indent():
                w('super().__init__(')

                with indent():
                    for field in message.field:
                        w(f'{field.name}={field.name},')

                w(')')

    def write_enum(self, enum_type):
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
                import_path = self._index.base_package.replace('/', '.') + '.' + self.import_name(file)
            else:
                import_path = self.import_name(file)

            w(f'import {import_path + protobuf_file_postfix} as \\')

            with self._import_buffer.indent():
                w(self.package_name(file) + protobuf_file_postfix)

        if self._import_requests:
            nl()

        nl()

    def write_add_fields_to_message(self, message):
        w = self._buffer.write

        if not message.field:
            return

        w('protox.add_fields_to_message(')

        with self._buffer.indent():
            w(f'{message.name},')
            for field in message.field:
                field_kwargs = {
                    'number': field.number
                }

                if is_message_field(field):
                    field_type = f'{self.resolve_field_type(field)}.as_field'
                elif is_enum_field(field):
                    field_type = 'protox.EnumField'
                    py_enum = self.resolve_field_type(field).strip("'")
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
                        field_kwargs['default'] = field.default_value

                if is_repeated(field):
                    if field.options.packed:
                        field_kwargs['packed'] = True

                    field_type = f'{field_type}.as_repeated'
                elif is_optional(field):
                    field_kwargs['required'] = 'False'
                else:
                    field_kwargs['required'] = 'True'

                w(f'{field.name}={field_type}(')

                with self._buffer.indent():
                    w(', '.join(
                        [
                            f'{key}={value}'
                            for key, value in field_kwargs.items()
                        ]
                    ))

                w('),')

        w(')\n')

    def generate(self) -> plugin_pb2.CodeGeneratorResponse.File:
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
            self.write_add_fields_to_message(message_type)

        self.write_imports()
        imports = self._import_buffer.read()
        content = self._buffer.read().strip('\n') + '\n'

        filename = (
            self._proto_file.name.strip().replace('.proto', '') +
            f'{protobuf_file_postfix}.py'
        )

        if self._index.base_package:
            filename = self._index.base_package + '/' + filename

        return plugin_pb2.CodeGeneratorResponse.File(
            name=filename,
            content=(
                imports +
                content
            ),
        )


def main():
    # data = b'\n\x0bgroup.proto\n\x0bhello.proto\n\nuser.proto\x12\x19base_package=app/protobuf\x1a\x08\x08\x03\x10\x06\x18\x01"\x00z\xf8\x01\n\x0bgroup.proto\x12\x0ccommon.types"*\n\x05Group"!\n\x06Status\x12\n\n\x06ACTIVE\x10\x01\x12\x0b\n\x07BLOCKED\x10\x02J\xae\x01\n\x06\x12\x04\x00\x00\t\x01\n\x08\n\x01\x0c\x12\x03\x00\x00\x12\n\x08\n\x01\x02\x12\x03\x02\x08\x14\n\n\n\x02\x04\x00\x12\x04\x04\x00\t\x01\n\n\n\x03\x04\x00\x01\x12\x03\x04\x08\r\n\x0c\n\x04\x04\x00\x04\x00\x12\x04\x05\x04\x08\x05\n\x0c\n\x05\x04\x00\x04\x00\x01\x12\x03\x05\t\x0f\n\r\n\x06\x04\x00\x04\x00\x02\x00\x12\x03\x06\x08\x13\n\x0e\n\x07\x04\x00\x04\x00\x02\x00\x01\x12\x03\x06\x08\x0e\n\x0e\n\x07\x04\x00\x04\x00\x02\x00\x02\x12\x03\x06\x11\x12\n\r\n\x06\x04\x00\x04\x00\x02\x01\x12\x03\x07\x08\x14\n\x0e\n\x07\x04\x00\x04\x00\x02\x01\x01\x12\x03\x07\x08\x0f\n\x0e\n\x07\x04\x00\x04\x00\x02\x01\x02\x12\x03\x07\x12\x13z\xfe\x02\n\nuser.proto\x12\x0ccommon.types\x1a\x0bgroup.proto"T\n\x04User\x12)\n\x05group\x18\x01 \x01(\x0b2\x13.common.types.GroupR\x05group"!\n\x06Status\x12\n\n\x06ACTIVE\x10\x01\x12\x0b\n\x07BLOCKED\x10\x02J\xfe\x01\n\x06\x12\x04\x00\x00\x0c\x01\n\x08\n\x01\x0c\x12\x03\x00\x00\x12\n\x08\n\x01\x02\x12\x03\x02\x08\x14\n\t\n\x02\x03\x00\x12\x03\x04\x07\x14\n\n\n\x02\x04\x00\x12\x04\x06\x00\x0c\x01\n\n\n\x03\x04\x00\x01\x12\x03\x06\x08\x0c\n\x0c\n\x04\x04\x00\x04\x00\x12\x04\x07\x04\n\x05\n\x0c\n\x05\x04\x00\x04\x00\x01\x12\x03\x07\t\x0f\n\r\n\x06\x04\x00\x04\x00\x02\x00\x12\x03\x08\x08\x13\n\x0e\n\x07\x04\x00\x04\x00\x02\x00\x01\x12\x03\x08\x08\x0e\n\x0e\n\x07\x04\x00\x04\x00\x02\x00\x02\x12\x03\x08\x11\x12\n\r\n\x06\x04\x00\x04\x00\x02\x01\x12\x03\t\x08\x14\n\x0e\n\x07\x04\x00\x04\x00\x02\x01\x01\x12\x03\t\x08\x0f\n\x0e\n\x07\x04\x00\x04\x00\x02\x01\x02\x12\x03\t\x12\x13\n\x0b\n\x04\x04\x00\x02\x00\x12\x03\x0b\x04\x1d\n\x0c\n\x05\x04\x00\x02\x00\x04\x12\x03\x0b\x04\x0c\n\x0c\n\x05\x04\x00\x02\x00\x06\x12\x03\x0b\r\x12\n\x0c\n\x05\x04\x00\x02\x00\x01\x12\x03\x0b\x13\x18\n\x0c\n\x05\x04\x00\x02\x00\x03\x12\x03\x0b\x1b\x1cz\xa2\x07\n\x0bhello.proto\x1a\nuser.proto"\xca\x01\n\x05Hello\x12\x14\n\x02id\x18\xe8\x07 \x02(\r:\x03123R\x02id\x12!\n\x05color\x18\x01 \x01(\x0e2\x06.Color:\x03REDR\x05color\x12/\n\x0ffavourite_color\x18\x02 \x03(\x0e2\x06.ColorR\x0efavouriteColor\x12\x1c\n\x07numbers\x18\n \x03(\x04B\x02\x10\x01R\x07numbers\x129\n\x06status\x18\x03 \x02(\x0e2\x19.common.types.User.Status:\x06ACTIVER\x06status*%\n\x05Color\x12\x07\n\x03RED\x10\x01\x12\t\n\x05GREEN\x10\x02\x12\x08\n\x04BLUE\x10\x03J\x92\x05\n\x06\x12\x04\x00\x00\x10\x01\n\x08\n\x01\x0c\x12\x03\x00\x00\x12\n\t\n\x02\x03\x00\x12\x03\x02\x07\x13\n\n\n\x02\x05\x00\x12\x04\x04\x00\x08\x01\n\n\n\x03\x05\x00\x01\x12\x03\x04\x05\n\n\x0b\n\x04\x05\x00\x02\x00\x12\x03\x05\x04\x0c\n\x0c\n\x05\x05\x00\x02\x00\x01\x12\x03\x05\x04\x07\n\x0c\n\x05\x05\x00\x02\x00\x02\x12\x03\x05\n\x0b\n\x0b\n\x04\x05\x00\x02\x01\x12\x03\x06\x04\x0e\n\x0c\n\x05\x05\x00\x02\x01\x01\x12\x03\x06\x04\t\n\x0c\n\x05\x05\x00\x02\x01\x02\x12\x03\x06\x0c\r\n\x0b\n\x04\x05\x00\x02\x02\x12\x03\x07\x04\r\n\x0c\n\x05\x05\x00\x02\x02\x01\x12\x03\x07\x04\x08\n\x0c\n\x05\x05\x00\x02\x02\x02\x12\x03\x07\x0b\x0c\n\n\n\x02\x04\x00\x12\x04\n\x00\x10\x01\n\n\n\x03\x04\x00\x01\x12\x03\n\x08\r\n\x0b\n\x04\x04\x00\x02\x00\x12\x03\x0b\x04,\n\x0c\n\x05\x04\x00\x02\x00\x04\x12\x03\x0b\x04\x0c\n\x0c\n\x05\x04\x00\x02\x00\x05\x12\x03\x0b\r\x13\n\x0c\n\x05\x04\x00\x02\x00\x01\x12\x03\x0b\x14\x16\n\x0c\n\x05\x04\x00\x02\x00\x03\x12\x03\x0b\x19\x1d\n\x0c\n\x05\x04\x00\x02\x00\x08\x12\x03\x0b\x1e+\n\x0c\n\x05\x04\x00\x02\x00\x07\x12\x03\x0b\'*\n\x0b\n\x04\x04\x00\x02\x01\x12\x03\x0c\x04+\n\x0c\n\x05\x04\x00\x02\x01\x04\x12\x03\x0c\x04\x0c\n\x0c\n\x05\x04\x00\x02\x01\x06\x12\x03\x0c\r\x12\n\x0c\n\x05\x04\x00\x02\x01\x01\x12\x03\x0c\x13\x18\n\x0c\n\x05\x04\x00\x02\x01\x03\x12\x03\x0c\x1b\x1c\n\x0c\n\x05\x04\x00\x02\x01\x08\x12\x03\x0c\x1d*\n\x0c\n\x05\x04\x00\x02\x01\x07\x12\x03\x0c&)\n\x0b\n\x04\x04\x00\x02\x02\x12\x03\r\x04\'\n\x0c\n\x05\x04\x00\x02\x02\x04\x12\x03\r\x04\x0c\n\x0c\n\x05\x04\x00\x02\x02\x06\x12\x03\r\r\x12\n\x0c\n\x05\x04\x00\x02\x02\x01\x12\x03\r\x13"\n\x0c\n\x05\x04\x00\x02\x02\x03\x12\x03\r%&\n\x0b\n\x04\x04\x00\x02\x03\x12\x03\x0e\x04/\n\x0c\n\x05\x04\x00\x02\x03\x04\x12\x03\x0e\x04\x0c\n\x0c\n\x05\x04\x00\x02\x03\x05\x12\x03\x0e\r\x13\n\x0c\n\x05\x04\x00\x02\x03\x01\x12\x03\x0e\x14\x1b\n\x0c\n\x05\x04\x00\x02\x03\x03\x12\x03\x0e\x1e \n\x0c\n\x05\x04\x00\x02\x03\x08\x12\x03\x0e!.\n\r\n\x06\x04\x00\x02\x03\x08\x02\x12\x03\x0e"-\n\x0b\n\x04\x04\x00\x02\x04\x12\x03\x0f\x04B\n\x0c\n\x05\x04\x00\x02\x04\x04\x12\x03\x0f\x04\x0c\n\x0c\n\x05\x04\x00\x02\x04\x06\x12\x03\x0f\r%\n\x0c\n\x05\x04\x00\x02\x04\x01\x12\x03\x0f&,\n\x0c\n\x05\x04\x00\x02\x04\x03\x12\x03\x0f/0\n\x0c\n\x05\x04\x00\x02\x04\x08\x12\x03\x0f1A\n\x0c\n\x05\x04\x00\x02\x04\x07\x12\x03\x0f:@'

    data = sys.stdin.buffer.read()
    # debug(data)
    # return

    # Parse request
    request = plugin_pb2.CodeGeneratorRequest()
    request.ParseFromString(data)
    index = Index(request)

    # Create response
    files_to_generate = set(request.file_to_generate)

    response = plugin_pb2.CodeGeneratorResponse(
        file=[
            CodeGenerator(proto_file, index).generate()
            for proto_file in request.proto_file
            if proto_file.name in files_to_generate
        ]
    )

    # for file in response.file:
    #     print('#', file.name)
    #     print(file.content)

    sys.stdout.buffer.write(
        response.SerializeToString()
    )


if __name__ == '__main__':
    main()