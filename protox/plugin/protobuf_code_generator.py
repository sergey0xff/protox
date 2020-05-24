from typing import Dict, Tuple

from protox import FileDescriptorProto, DescriptorProto, FieldDescriptorProto, EnumDescriptorProto
from protox.plugin.common import StringBuffer, FieldMangler, is_well_known_type_field, is_enum_field, \
    PROTOBUF_FILE_POSTFIX, is_message_field, is_repeated, is_map_message, pb_to_protox_type, is_group_field, \
    pb_to_py_type, is_optional, is_empty_message, collect_one_of, pythonize_default_value, fix_redundant_newlines, \
    pb_type_to_zero_value
from protox.plugin.index import Index
from protox.well_known_types.plugin import CodeGeneratorResponse


class ProtobufCodeGenerator:
    def __init__(
        self,
        proto_file: FileDescriptorProto,
        index: Index,
    ):
        self._proto_file: FileDescriptorProto = proto_file
        self._index: Index = index
        self._indent: int = 0
        self._uses_enums: bool = False
        self._uses_typing: bool = False
        self._import_requests: Dict[str, FileDescriptorProto] = {}
        self._buffer = StringBuffer()
        self._import_buffer = StringBuffer()
        self._field_manglers: Dict[str, FieldMangler] = {}

    @property
    def is_proto3(self) -> bool:
        return self._proto_file.syntax == 'proto3'

    @property
    def proto_file(self):
        return self._proto_file

    @property
    def index(self):
        return self._index

    def empty(self) -> bool:
        return not (
            self._proto_file.enum_type or
            self._proto_file.message_type
        )

    def has_services(self) -> bool:
        return bool(self._proto_file.service)

    def has_messages(self) -> bool:
        return bool(self._proto_file.message_type)

    def resolve_field_name(self, message: DescriptorProto, field: str) -> str:
        if message.name not in self._field_manglers:
            self._field_manglers[message.name] = FieldMangler(
                message,
            )

        return self._field_manglers[message.name].get(field)

    def is_local_type(self, type_name: str):
        """
        :param type_name message or enum type
        Checks if py_type defined in current file
        """
        return self._index.proto_files[type_name] == self._proto_file

    def get_local_type(self, type_name: str) -> str:
        field_type = type_name.lstrip('.')
        field_type = field_type[len(self._proto_file.package or ''):]
        field_type = field_type.lstrip('.')

        return field_type

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
            PROTOBUF_FILE_POSTFIX.rstrip('.') +
            '.' +
            field_type[1 + len(file.package or ''):].lstrip('.')
        )

        return imported_name

    def is_map_field(self, field: FieldDescriptorProto) -> bool:
        if not is_message_field(field):
            return False

        if not is_repeated(field):
            return False

        return is_map_message(
            self._index.messages[field.type_name]
        )

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
            if self.is_local_type(message.field[1].type_name):
                value_type = self.get_local_type(message.field[1].type_name)
            else:
                value_type = self.resolve_field_import(message.field[1])
        elif is_enum_field(message.field[1]):
            field = message.field[1]

            if self.is_local_type(field.type_name):
                value_type = self.get_local_type(field.type_name)
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
                py_type = f"'{self.get_local_type(field.type_name)}'"
            else:
                py_type = self.resolve_field_import(field)
        elif is_enum_field(field):
            if self.is_local_type(field.type_name):
                py_type = f"'{self.get_local_type(field.type_name)}'"
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
                if not is_map_message(nested_type):
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

    @property
    def preamble(self) -> str:
        return (
            '# Generated by protox. DO NOT EDIT!\n'
            f'# source: {self._proto_file.name}'
        )

    def write_preamble(self):
        self._import_buffer.write(self.preamble)

    def write_imports(self):
        w = self._import_buffer.write
        nl = self._import_buffer.nl

        if self._uses_typing:
            w('import typing')

        if self._uses_enums:
            w('from enum import IntEnum')

        if self._uses_enums or self._uses_typing:
            nl()

        if self.has_messages():
            w('import protox\n')

        for file in self._import_requests.values():
            if self._index.base_package:
                import_path = self._index.base_package.replace('/', '.') + '.' + self.file_to_import_name(file)
            else:
                import_path = self.file_to_import_name(file)

            w(f'import {import_path + PROTOBUF_FILE_POSTFIX} as \\')

            with self._import_buffer.indent():
                w(self.file_to_package_name(file) + PROTOBUF_FILE_POSTFIX)

        if self._import_requests:
            nl()

        nl()

    def write_define_fields(self, message: DescriptorProto, path: str = ''):
        w = self._buffer.write
        message_full_name = path + message.name

        for nested_type in message.nested_type:
            if is_map_message(nested_type):
                continue

            self.write_define_fields(
                nested_type,
                path=path + message.name + '.',
            )

        if not message.field:
            return

        w('protox.define_fields(')

        with self._buffer.indent():
            w(message_full_name, ',')

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
                    elif self.is_proto3 and not is_repeated(field):
                        field_kwargs['default'] = 0
                elif is_group_field(field):
                    raise NotImplementedError(
                        'Groups are not supported yet'
                    )
                else:
                    field_type = f'protox.{pb_to_protox_type(field.type)}'

                    if field.default_value:
                        field_kwargs['default'] = pythonize_default_value(
                            field.default_value,
                            field.type,
                        )
                    elif self.is_proto3 and not is_repeated(field):
                        field_kwargs['default'] = pb_type_to_zero_value(
                            field.type
                        )

                if self.is_map_field(field):
                    # map and message fields has no default or required params
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

        w(')')
        w(
            message_full_name,
            f'.DESCRIPTOR = protox.DescriptorProto.from_bytes(',
            repr(message.to_bytes()),
            ')',
        )
        w(
            message_full_name,
            '.DESCRIPTOR.file_descriptor = FILE_DESCRIPTOR',
        )

        package = self._proto_file.package

        if package:
            qualified_message_name = package.lstrip('.') + '.' + message.name
        else:
            qualified_message_name = message.name

        w(
            message_full_name,
            '.DESCRIPTOR.full_name = ',
            "'",
            qualified_message_name,
            "'",
            '\n'
        )

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

        self._buffer.write(
            'FILE_DESCRIPTOR = protox.FileDescriptorProto.from_bytes(',
            repr(self._proto_file.to_bytes()),
            ')',
            '\n',
        )

        # message fields
        for message_type in self._proto_file.message_type:
            self.write_define_fields(message_type)

        self.write_preamble()
        self.write_imports()
        imports = self._import_buffer.read()
        content = self._buffer.read().strip('\n') + '\n'

        return CodeGeneratorResponse.File(
            name=self.get_file_name(PROTOBUF_FILE_POSTFIX),
            content=fix_redundant_newlines(
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
