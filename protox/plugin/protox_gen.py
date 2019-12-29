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


def is_well_known_type_field(field):
    return field.type_name.startswith('.google.protobuf')


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

    @staticmethod
    def resolve_google_protobuf_import(field):
        type_name = field.type_name.split(".")[-1]
        return f'protox.{type_name}'

    def resolve_import(self, field):
        """
        Requests import of the file in which the imported message is
        """
        if is_well_known_type_field(field):
            return self.resolve_google_protobuf_import(field)

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

            if self.write_oneofs(message):
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
        one_ofs = collect_one_of(message).items()

        for name, fields in one_ofs:
            w(f'{name} = protox.one_of(')

            with self._buffer.indent():
                for field in fields:
                    w(f"'{field}',")

            w(')')

        return bool(one_ofs)

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

        if self._proto_file.enum_type:
            nl(2)

        # messages
        for message_type in self._proto_file.message_type:
            self.write_message(message_type)

        if self._proto_file.message_type:
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
    # data = b'\n\x12hello_protox.proto\x12\x19base_package=app/protobuf\x1a\x08\x08\x03\x10\x06\x18\x01"\x00z\xb8\x12\n\x1bgoogle/protobuf/empty.proto\x12\x0fgoogle.protobuf"\x07\n\x05EmptyBv\n\x13com.google.protobufB\nEmptyProtoP\x01Z\'github.com/golang/protobuf/ptypes/empty\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypesJ\xfe\x10\n\x06\x12\x04\x1e\x003\x10\n\xcc\x0c\n\x01\x0c\x12\x03\x1e\x00\x122\xc1\x0c Protocol Buffers - Google\'s data interchange format\n Copyright 2008 Google Inc.  All rights reserved.\n https://developers.google.com/protocol-buffers/\n\n Redistribution and use in source and binary forms, with or without\n modification, are permitted provided that the following conditions are\n met:\n\n     * Redistributions of source code must retain the above copyright\n notice, this list of conditions and the following disclaimer.\n     * Redistributions in binary form must reproduce the above\n copyright notice, this list of conditions and the following disclaimer\n in the documentation and/or other materials provided with the\n distribution.\n     * Neither the name of Google Inc. nor the names of its\n contributors may be used to endorse or promote products derived from\n this software without specific prior written permission.\n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS\n "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT\n LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR\n A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT\n OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,\n SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT\n LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,\n DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY\n THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT\n (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE\n OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n\n\x08\n\x01\x02\x12\x03 \x08\x17\n\x08\n\x01\x08\x12\x03"\x00;\n\t\n\x02\x08%\x12\x03"\x00;\n\x08\n\x01\x08\x12\x03#\x00>\n\t\n\x02\x08\x0b\x12\x03#\x00>\n\x08\n\x01\x08\x12\x03$\x00,\n\t\n\x02\x08\x01\x12\x03$\x00,\n\x08\n\x01\x08\x12\x03%\x00+\n\t\n\x02\x08\x08\x12\x03%\x00+\n\x08\n\x01\x08\x12\x03&\x00"\n\t\n\x02\x08\n\x12\x03&\x00"\n\x08\n\x01\x08\x12\x03\'\x00!\n\t\n\x02\x08$\x12\x03\'\x00!\n\x08\n\x01\x08\x12\x03(\x00\x1f\n\t\n\x02\x08\x1f\x12\x03(\x00\x1f\n\xfb\x02\n\x02\x04\x00\x12\x033\x00\x10\x1a\xef\x02 A generic empty message that you can re-use to avoid defining duplicated\n empty messages in your APIs. A typical example is to use it as the request\n or the response type of an API method. For instance:\n\n     service Foo {\n       rpc Bar(google.protobuf.Empty) returns (google.protobuf.Empty);\n     }\n\n The JSON representation for `Empty` is empty JSON object `{}`.\n\n\n\n\x03\x04\x00\x01\x12\x033\x08\rb\x06proto3z\xe8\x01\n\x12hello_protox.proto\x1a\x1bgoogle/protobuf/empty.proto"9\n\tMyMessage\x12,\n\x05empty\x18\x01 \x02(\x0b2\x16.google.protobuf.EmptyR\x05emptyJz\n\x06\x12\x04\x00\x00\x06\x01\n\x08\n\x01\x0c\x12\x03\x00\x00\x12\n\t\n\x02\x03\x00\x12\x03\x02\x07$\n\n\n\x02\x04\x00\x12\x04\x04\x00\x06\x01\n\n\n\x03\x04\x00\x01\x12\x03\x04\x08\x11\n\x0b\n\x04\x04\x00\x02\x00\x12\x03\x05\x04-\n\x0c\n\x05\x04\x00\x02\x00\x04\x12\x03\x05\x04\x0c\n\x0c\n\x05\x04\x00\x02\x00\x06\x12\x03\x05\r"\n\x0c\n\x05\x04\x00\x02\x00\x01\x12\x03\x05#(\n\x0c\n\x05\x04\x00\x02\x00\x03\x12\x03\x05+,'

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
            # TODO: refactor the following line
            if proto_file.name in files_to_generate and not proto_file.name.startswith('google/protobuf/')
        ]
    )

    sys.stdout.buffer.write(
        response.SerializeToString()
    )


if __name__ == '__main__':
    main()
