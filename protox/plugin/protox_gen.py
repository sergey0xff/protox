#!/usr/bin/env python3
import sys
from contextlib import contextmanager
from typing import List, Dict

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


def collect_one_of(message) -> Dict[str, List[str]]:
    one_ofs = {}
    one_of_by_index = []

    for one_of in message.oneof_decl:
        lst = []
        one_ofs[one_of.name] = lst
        one_of_by_index.append(lst)

    for field in message.field:
        if field.HasField('oneof_index'):
            one_of_by_index[field.oneof_index].append(field.name)

    return one_ofs


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

    def is_map_field(self, field) -> bool:
        if not is_message_field(field):
            return False

        if not is_repeated(field):
            return False

        return self.is_map_message(
            self._index.messages[field.type_name]
        )

    def is_map_message(self, message) -> bool:
        return bool(message.options.map_entry)

    def map_message_py_types(self, message):
        key_type = self.resolve_field_type(message.field[0])
        value_type = self.resolve_field_type(message.field[1])
        return key_type, value_type

    def map_message_protox_types(self, message):
        if is_message_field(message.field[0]):
            key_type = self.resolve_import(message.field[0])
        else:
            key_type = 'protox.' + pb_to_protox_type(message.field[0].type)

        if is_message_field(message.field[1]):
            value_type = self.resolve_import(message.field[1])
        elif is_enum_field(message.field[1]):
            field = message.field[1]
            path = '.'.join(field.type_name.split('.')[:-1])

            if self.is_local_type(path):
                value_type = field.type_name.lstrip('.')
            else:
                value_type = self.resolve_import(field)
        else:
            value_type = 'protox.' + pb_to_protox_type(message.field[1].type)

        return key_type, value_type

    def resolve_field_type(self, field):
        if self.is_map_field(field):
            message = self._index.messages[field.type_name]
            key_type, value_type = self.map_message_py_types(message)
            py_type = f'typing.Dict[{key_type}, {value_type}]'
            self._uses_typing = True
        elif is_message_field(field):
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
        if self.is_map_field(field):
            self._uses_typing = True
        elif is_optional(field):
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
                w(f'{field.name}: {py_type}')

            nl()

            self.write_oneofs(message)
            nl()

            self.write_init(message)

    def write_init(self, message):
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

                w(f'{field.name}: {py_type} = None,')

        w('):')

        with indent():
            w('super().__init__(')

            with indent():
                for field in message.field:
                    w(f'{field.name}={field.name},')

            w(')')

    def write_oneofs(self, message):
        w = self._buffer.write
        for name, fields in collect_one_of(message).items():
            w(f'{name} = protox.one_of(')

            with self._buffer.indent():
                for field in fields:
                    w(f"'{field}',")

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

        w('protox.define_fields(')

        with self._buffer.indent():
            w(f'{message.name},')
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

                if self.is_map_field(field):
                    pass
                elif is_repeated(field):
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
    # data = b'\n\x12hello_protox.proto\x12\x19base_package=app/protobuf\x1a\x08\x08\x03\x10\x06\x18\x01"\x00z\xd2\x07\n\x12hello_protox.proto"\xaa\x02\n\x04User\x12\x0e\n\x02id\x18\x01 \x02(\rR\x02id\x12\x12\n\x04name\x18\x02 \x02(\tR\x04name\x12+\n\x04type\x18\x03 \x02(\x0e2\n.User.Type:\x0bMERE_MORTALR\x04type\x12&\n\x05props\x18\x04 \x03(\x0b2\x10.User.PropsEntryR\x05props\x12\x10\n\x02ok\x18\n \x01(\x05H\x00R\x02ok\x12\x14\n\x04fail\x18\x0b \x01(\x05H\x00R\x04fail\x1aD\n\nPropsEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12 \n\x05value\x18\x02 \x01(\x0e2\n.User.TypeR\x05value:\x028\x01"1\n\x04Type\x12\r\n\tUNDEFINED\x10\x00\x12\x0f\n\x0bMERE_MORTAL\x10\x01\x12\t\n\x05ADMIN\x10\x02B\x08\n\x06resultJ\x8e\x05\n\x06\x12\x04\x00\x00\x12\x01\n\x08\n\x01\x0c\x12\x03\x00\x00\x12\n\n\n\x02\x04\x00\x12\x04\x02\x00\x12\x01\n\n\n\x03\x04\x00\x01\x12\x03\x02\x08\x0c\n\x0c\n\x04\x04\x00\x04\x00\x12\x04\x03\x04\x07\x05\n\x0c\n\x05\x04\x00\x04\x00\x01\x12\x03\x03\t\r\n\r\n\x06\x04\x00\x04\x00\x02\x00\x12\x03\x04\x08\x16\n\x0e\n\x07\x04\x00\x04\x00\x02\x00\x01\x12\x03\x04\x08\x11\n\x0e\n\x07\x04\x00\x04\x00\x02\x00\x02\x12\x03\x04\x14\x15\n\r\n\x06\x04\x00\x04\x00\x02\x01\x12\x03\x05\x08\x18\n\x0e\n\x07\x04\x00\x04\x00\x02\x01\x01\x12\x03\x05\x08\x13\n\x0e\n\x07\x04\x00\x04\x00\x02\x01\x02\x12\x03\x05\x16\x17\n\r\n\x06\x04\x00\x04\x00\x02\x02\x12\x03\x06\x08\x12\n\x0e\n\x07\x04\x00\x04\x00\x02\x02\x01\x12\x03\x06\x08\r\n\x0e\n\x07\x04\x00\x04\x00\x02\x02\x02\x12\x03\x06\x10\x11\n\x0b\n\x04\x04\x00\x02\x00\x12\x03\t\x04\x1b\n\x0c\n\x05\x04\x00\x02\x00\x04\x12\x03\t\x04\x0c\n\x0c\n\x05\x04\x00\x02\x00\x05\x12\x03\t\r\x13\n\x0c\n\x05\x04\x00\x02\x00\x01\x12\x03\t\x14\x16\n\x0c\n\x05\x04\x00\x02\x00\x03\x12\x03\t\x19\x1a\n\x0b\n\x04\x04\x00\x02\x01\x12\x03\n\x04\x1d\n\x0c\n\x05\x04\x00\x02\x01\x04\x12\x03\n\x04\x0c\n\x0c\n\x05\x04\x00\x02\x01\x05\x12\x03\n\r\x13\n\x0c\n\x05\x04\x00\x02\x01\x01\x12\x03\n\x14\x18\n\x0c\n\x05\x04\x00\x02\x01\x03\x12\x03\n\x1b\x1c\n\x0b\n\x04\x04\x00\x02\x02\x12\x03\x0b\x043\n\x0c\n\x05\x04\x00\x02\x02\x04\x12\x03\x0b\x04\x0c\n\x0c\n\x05\x04\x00\x02\x02\x06\x12\x03\x0b\r\x11\n\x0c\n\x05\x04\x00\x02\x02\x01\x12\x03\x0b\x12\x16\n\x0c\n\x05\x04\x00\x02\x02\x03\x12\x03\x0b\x19\x1a\n\x0c\n\x05\x04\x00\x02\x02\x08\x12\x03\x0b\x1b2\n\x0c\n\x05\x04\x00\x02\x02\x07\x12\x03\x0b&1\n\x0b\n\x04\x04\x00\x02\x03\x12\x03\x0c\x04 \n\r\n\x05\x04\x00\x02\x03\x04\x12\x04\x0c\x04\x0b3\n\x0c\n\x05\x04\x00\x02\x03\x06\x12\x03\x0c\x04\x15\n\x0c\n\x05\x04\x00\x02\x03\x01\x12\x03\x0c\x16\x1b\n\x0c\n\x05\x04\x00\x02\x03\x03\x12\x03\x0c\x1e\x1f\n\x0c\n\x04\x04\x00\x08\x00\x12\x04\x0e\x04\x11\x05\n\x0c\n\x05\x04\x00\x08\x00\x01\x12\x03\x0e\n\x10\n\x0b\n\x04\x04\x00\x02\x04\x12\x03\x0f\x08\x16\n\x0c\n\x05\x04\x00\x02\x04\x05\x12\x03\x0f\x08\r\n\x0c\n\x05\x04\x00\x02\x04\x01\x12\x03\x0f\x0e\x10\n\x0c\n\x05\x04\x00\x02\x04\x03\x12\x03\x0f\x13\x15\n\x0b\n\x04\x04\x00\x02\x05\x12\x03\x10\x08\x18\n\x0c\n\x05\x04\x00\x02\x05\x05\x12\x03\x10\x08\r\n\x0c\n\x05\x04\x00\x02\x05\x01\x12\x03\x10\x0e\x12\n\x0c\n\x05\x04\x00\x02\x05\x03\x12\x03\x10\x15\x17'

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

    sys.stdout.buffer.write(
        response.SerializeToString()
    )


if __name__ == '__main__':
    main()
