import re
from collections import Counter
from contextlib import contextmanager
from typing import Dict, List, Union

from protox import DescriptorProto, FieldDescriptorProto, Message

MESSAGE_PROPS = set(dir(Message))
RESERVED_NAMES = {
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

    'IntEnum',

    # protox.Message special names
    '__message_type__',

    *MESSAGE_PROPS,
}
PROTOBUF_FILE_POSTFIX = '_pb'
GRPCLIB_FILE_POSTFIX = '_grpclib'


def pythonize_name(name: str) -> str:
    if name in RESERVED_NAMES:
        return name + '_'

    return name


def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def fix_redundant_newlines(text: str) -> str:
    return re.sub(r'\n{3,}', '\n\n\n', text)


def is_empty_message(message: DescriptorProto) -> bool:
    return not (
        message.nested_type or
        message.field or
        message.enum_type
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


def pb_type_to_zero_value(
    pb_type: FieldDescriptorProto.Type
) -> Union[int, float, str, bool, bytes]:
    fd = FieldDescriptorProto.Type

    return {
        fd.TYPE_DOUBLE: 0.0,
        fd.TYPE_FLOAT: 0.0,

        fd.TYPE_INT64: 0,
        fd.TYPE_UINT64: 0,
        fd.TYPE_INT32: 0,
        fd.TYPE_UINT32: 0,
        fd.TYPE_FIXED64: 0,
        fd.TYPE_FIXED32: 0,
        fd.TYPE_SFIXED32: 0,
        fd.TYPE_SFIXED64: 0,
        fd.TYPE_SINT32: 0,
        fd.TYPE_SINT64: 0,

        fd.TYPE_STRING: "''",
        fd.TYPE_BYTES: "b''",

        fd.TYPE_BOOL: 'False',
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


def pythonize_default_value(
    default_value: str,
    field_type: FieldDescriptorProto.Type
) -> str:
    if field_type == FieldDescriptorProto.Type.TYPE_STRING:
        return f"'{default_value}'"

    if field_type == FieldDescriptorProto.Type.TYPE_BYTES:
        return f"b'{default_value}'"

    if field_type == FieldDescriptorProto.Type.TYPE_BOOL:
        return {
            'true': 'True',
            'false': 'False',
        }[default_value]

    return default_value


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


def is_map_message(message: DescriptorProto) -> bool:
    try:
        return bool(message.options.map_entry)
    except AttributeError:
        return False


def is_well_known_type_field(type_name: str) -> bool:
    return type_name.startswith('.google.protobuf')


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


class FieldMangler:
    def __init__(self, message: DescriptorProto):
        # original field names
        self._message_fields = set(
            x.name for x in message.field
        )
        self._name_counter = Counter()

        # maps original field names to mangled ones
        self._mangled_names: Dict[str, str] = {}

        for name in self._message_fields:
            self._process_name(name)

    def _mangle_name(self, name: str) -> str:
        self._name_counter[name] += 1

        while f'{name}_{self._name_counter[name]}' in self._message_fields:
            self._name_counter[name] += 1

        counter = self._name_counter[name]

        if counter == 1:
            counter = ''

        return f'{name}_{counter}'

    def _process_name(self, name: str):
        py_name = to_snake_case(name)

        if (
            py_name in RESERVED_NAMES
            or
            py_name != name and py_name in self._message_fields
        ):
            py_name = self._mangle_name(py_name)

        self._mangled_names[name] = py_name

    def get(self, field: str) -> str:
        if field not in self._message_fields:
            raise ValueError('No such name')

        return self._mangled_names[field]
