import io
from abc import ABCMeta
from enum import IntEnum
from typing import BinaryIO, List, Callable, Optional, TypeVar, Type, Dict, Union, Set

from protox.encoding import decode_header, wire_type_to_decoder
from protox.exceptions import MessageEncodeError, MessageDecodeError, FieldValidationError
from protox.fields import Field, OneOf, Repeated, MessageField, MapField, PrimitiveField
from protox.validated_dict import ValidatedDict
from protox.validated_list import ValidatedList

if False:
    from protox.well_known_types.descriptor import DescriptorProto  # noqa

__all__ = [
    'Message',
    'define_fields',
]


class FieldGetter:
    def __init__(self, key: str, default=None):
        self._key = key
        self._default = default

    def __call__(self, obj):
        return obj._data.get(self._key, self._default)


class FieldSetter:
    def __init__(self, key):
        self._key = key

    def __call__(self, obj, value):
        obj._field_by_name[self._key].validate_value(value)
        obj._data[self._key] = value


class RepeatedSetter:
    def __init__(self, key, field):
        self._key = key
        self._field = field

    def __call__(self, obj, value):
        obj._field_by_name[self._key].validate_value(value)
        obj._data[self._key] = ValidatedList(self._field, value)


class RepeatedGetter:
    def __init__(self, key, field):
        self._key = key
        self._field = field

    def __call__(self, obj):
        obj._data.setdefault(self._key, ValidatedList(self._field))
        return obj._data[self._key]


class MapSetter:
    def __init__(self, key, field: MapField):
        self._key = key
        self._field = field

    def __call__(self, obj, value):
        obj._field_by_name[self._key].validate_value(value)
        obj._data[self._key] = ValidatedDict(
            self._field,
            value
        )


class MapGetter:
    def __init__(self, key, field: MapField):
        self._key = key
        self._field = field

    def __call__(self, obj):
        obj._data.setdefault(self._key, ValidatedDict(self._field))
        return obj._data[self._key]


class OneOfSetter(FieldSetter):
    def __init__(self, key, one_of: OneOf):
        super().__init__(key)
        self._one_of_name = one_of.name
        self._one_of_fields: List[str] = one_of.fields

    def __call__(self, obj, value):
        obj._field_by_name[self._key].validate_value(value)

        for name in self._one_of_fields:
            obj._data.pop(name, None)

        obj._data[self._key] = value
        obj._which_one_of[self._one_of_name] = self._key


def _add_field_to_message(
    message_type: Type['Message'],
    name: str,
    field: Field
):
    if isinstance(field, Repeated):
        field_getter = RepeatedGetter(name, field.field)
    elif isinstance(field, MapField):
        field_getter = MapGetter(name, field)
    elif isinstance(field, MessageField):
        # TODO: probably replace with MessageGetter
        field_getter = FieldGetter(name, None)
    elif isinstance(field, PrimitiveField):
        field_getter = FieldGetter(name, field.default)
    else:
        raise Exception('Unreachable code')

    if name in message_type._one_of_by_field_name:
        if getattr(field, 'required', False):
            raise FieldValidationError(
                f'A one_of field {message_type.__name__}.{name} should be optional, not required!'
            )

        field_setter = OneOfSetter(name, message_type._one_of_by_field_name[name])
    elif isinstance(field, MapField):
        field_setter = MapSetter(name, field)
    elif isinstance(field, Repeated):
        field_setter = RepeatedSetter(name, field.field)
    else:
        field_setter = FieldSetter(name)

    message_type._field_by_name[name] = field
    message_type._field_by_number[field.number] = field

    field.name = name

    if (
        getattr(field, 'required', False)
        and getattr(field, 'default', None) is None
    ):
        message_type._required_fields.add(field.name)

    setattr(
        message_type,
        name,
        property(
            field_getter,
            field_setter,
        )
    )


def define_fields(
    # using this mangled name to avoid field name conflict
    __message_type__: Type['Message'],
    **kwargs,
):
    for name, field in kwargs.items():
        _add_field_to_message(
            __message_type__,
            name,
            field,
        )


class MessageMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        new_cls = super().__new__(
            mcs,
            name,
            bases,
            namespace,
        )

        if name != 'Message':
            fields = mcs._collect_fields(name, namespace)

            new_cls._field_by_name = {}
            new_cls._field_by_number = {}
            new_cls._required_fields = set()

            one_ofs = mcs._collect_one_ofs(name, namespace)
            new_cls._one_of_by_field_name = one_ofs
            new_cls._one_ofs = {x.name for x in one_ofs.values()}

            define_fields(new_cls, **fields)

        return new_cls

    @classmethod
    def _collect_one_ofs(mcs, class_name: str, class_dict: dict) -> Dict[str, OneOf]:
        one_ofs = {}

        for key, value in class_dict.items():
            if isinstance(value, OneOf):
                value.name = key

                if len(value.fields) < 1:
                    raise FieldValidationError(
                        f'one_f {key!r} of message {class_name!r} should have at least one field'
                    )

                for name in value.fields:
                    one_ofs[name] = value

        return one_ofs

    @classmethod
    def _collect_fields(mcs, class_name: str, class_dict: dict) -> dict:
        fields = {}
        field_numbers = set()

        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key

                if value.number in field_numbers:
                    raise FieldValidationError(
                        f'Field with number {value.number} is already registered in message {class_name!r}'
                    )

                field_numbers.add(value.number)

                if hasattr(value, 'default') and value.default is not None:
                    try:
                        value.validate_value(value.default)
                    except ValueError:
                        raise FieldValidationError(
                            f'Field {key!r} of message {class_name!r} has invalid default value: {value.default!r}'
                        )

                fields[key] = value

        return fields


T = TypeVar('T')


class Message(metaclass=MessageMeta):
    # The following fields provided by metaclass
    _field_by_name: Dict[str, Union[Field, Repeated]] = None
    _field_by_number: Dict[int, Union[Field, Repeated]] = None
    _one_of_by_field_name: dict = None
    _required_fields: Set[str] = None

    # Provided by code generator
    DESCRIPTOR: 'DescriptorProto' = None

    _to_python: Optional[Callable] = None
    _from_python: Optional[Callable] = None

    def __init__(self, **kwargs):
        """
        :raises:
            AttributeError: when messages has no such field
            ValueError: when field value is invalid
        """
        self._data = {}
        self._which_one_of = {}

        for key, value in kwargs.items():
            if key not in self._field_by_name:
                raise AttributeError(
                    f'Protocol message {type(self).__qualname__} has no {key!r} field'
                )
            if value is not None:
                setattr(self, key, value)

    def to_python(self):
        if self._to_python is None:
            raise NotImplementedError(
                f'to_python() function is not provided for protocol message {type(self).__qualname__}'
            )

        return self._to_python()

    @classmethod
    def from_python(cls: Type[T], value) -> T:
        if cls._from_python is None:
            raise NotImplementedError(
                f'from_python() function is not provided for protocol message {cls.__qualname__}'
            )
        return cls._from_python(value)

    @classmethod
    def set_to_python(cls, fn: Callable):
        cls._to_python = fn

    @classmethod
    def set_from_python(cls, fn: Callable):
        cls._from_python = fn

    @classmethod
    def as_field(cls, *, number: int, required: bool = False) -> MessageField:
        return MessageField(
            cls,
            number=number,
            required=required,
        )

    @classmethod
    def as_repeated(cls, *, number: int) -> Repeated:
        return Repeated(
            cls,
            number=number
        )

    @classmethod
    def from_bytes(cls: Type[T], data: bytes, *, strict=True) -> T:
        stream = io.BytesIO(data)
        return cls.from_stream(stream, strict=strict)

    @classmethod
    def from_stream(cls: Type[T], stream: BinaryIO, *, strict=True) -> T:
        """
        :param stream:
        :param strict: when strict is False MessageDecodeError won't be raised in case a required field was not read
        :return: Message of type T
        """
        message_fields = {}

        while True:
            # checking for end of message
            try:
                number, wire_type = decode_header(stream)
            except MessageDecodeError:
                break

            if number in cls._field_by_number:
                field = cls._field_by_number[number]

                if field.wire_type != wire_type:
                    raise MessageDecodeError(
                        f"Field {field.name} has wire_type={field.wire_type}, "
                        f"read wire_type={wire_type} instead"
                    )

                if isinstance(field, Repeated) and not field.packed:
                    message_fields.setdefault(field.name, []).append(field.decode(stream))
                elif isinstance(field, MapField):
                    key, value = field.decode(stream)
                    message_fields.setdefault(field.name, {})[key] = value
                elif isinstance(field, MessageField):
                    message_fields[field.name] = field.decode(stream, strict=strict)
                else:
                    message_fields[field.name] = field.decode(stream)
            else:
                # read and discard unknown field
                wire_type_to_decoder[wire_type](stream)

        if strict:
            # TODO: when adding field to Message if the field is required
            #  put it to Message._required_fields to simplify the following check
            for key, field, in cls._field_by_name.items():
                if getattr(field, 'required', False) and not getattr(field, 'default', None) and key not in message_fields:
                    raise MessageDecodeError(
                        f"Missing required field {key}"
                    )

        return cls(**message_fields)

    def to_bytes(self) -> bytes:
        stream = io.BytesIO()
        self.to_stream(stream)
        stream.seek(0)
        return stream.read()

    def to_stream(self, stream: BinaryIO):
        if not self.is_initialized():
            required_fields = self._required_fields - self._data.keys()

            raise MessageEncodeError(
                f'Message {type(self).__qualname__!r} is missing required fields: {", ".join(required_fields)}'
            )

        for key, field in self._field_by_name.items():
            value = getattr(self, key)

            if value is None and not getattr(field, 'required', False):
                continue

            stream.write(field.encode(value))

    def has_field(self, name: str) -> bool:
        """
        Checks if field was explicitly set

        :raises:
            AttributeError: if message has no such field
        """
        if name not in self._field_by_name:
            raise AttributeError(
                f"Protocol message {type(self).__qualname__} has no such field {name!r}"
            )

        return name in self._data

    def which_one_of(self, one_of_name: str) -> Optional[str]:
        if one_of_name not in self._one_ofs:
            raise ValueError(
                f'Protocol message {type(self).__qualname__} has no such one_of {one_of_name!r}'
            )

        try:
            return self._which_one_of[one_of_name]
        except KeyError:
            return None

    def is_empty(self) -> bool:
        """
        Returns False if at least one field was explicitly set
        """
        return not bool(self._data)

    def is_initialized(self) -> bool:
        """
        Returns True if all required non-default fields are set
        """
        return self._required_fields.issubset(
            self._data.keys()
        )

    @classmethod
    def list_fields(cls) -> List[str]:
        return list(cls._field_by_name.keys())

    def to_dict(self) -> dict:
        data = {}

        for key, value in self._data.items():
            data[key] = self._to_dict(value)

        return data

    def _to_dict(self, value):
        if isinstance(value, Message):
            return value.to_dict()

        if isinstance(value, List):
            return [self._to_dict(x) for x in value]

        if isinstance(value, Dict):
            return dict(value)

        return value

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(
                f'Cannot compare protocol message {type(self).__qualname__} '
                f'to {type(other).__qualname__}'
            )

        return all(
            getattr(self, field) == getattr(other, field)
            for field in self.list_fields()
        )

    def __ne__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(
                f'Cannot compare protocol message {type(self).__qualname__} '
                f'to {type(self)}'
            )

        return not self == other

    def __str__(self):
        return self._format()

    _format_indent = ' ' * 4

    def _format(self, buffer: list = None, indent_level=0) -> str:
        buffer = buffer or []

        if indent_level == 0:
            buffer.append(f"message {type(self).__name__}")

        for key, value in self._data.items():
            self._format_value(key, value, buffer, indent_level + 1)

        return '\n'.join(buffer)

    def _format_nested_message(
        self,
        buffer: list,
        name: str,
        value: 'Message',
        indent_level: int,
    ):
        indent = self._format_indent * indent_level
        buffer.append(f'{indent}{name} = {type(value).__name__} {{')
        value._format(buffer, indent_level)
        buffer.append(f'{indent}}}')

    def _format_enum(
        self,
        buffer: list,
        name: str,
        value: IntEnum,
        indent_level: int,
    ):
        indent = self._format_indent * indent_level
        buffer.append(f'{indent}{name + " =" if name else ""} {str(value)}')

    def _format_repeated(
        self,
        buffer: list,
        name: str,
        value: list,
        indent_level: int,
    ):
        indent = self._format_indent * indent_level
        buffer.append(f'{indent}{name} = [')
        nested_indent = indent + self._format_indent
        first_n_items = 10

        for item in value[:first_n_items]:
            if isinstance(item, Message):
                if item.is_empty():
                    buffer.append(f'{nested_indent}{{}}')
                else:
                    buffer.append(f'{nested_indent}{{')
                    item._format(buffer, indent_level + 1)
                    buffer.append(f'{nested_indent}}}')
            else:
                self._format_value('', item, buffer, indent_level + 1)

        if len(value) > first_n_items:
            buffer.append(f'{nested_indent}... items more: {len(value) - first_n_items}')

        buffer.append(f'{indent}]')

    def _format_map(
        self,
        buffer: list,
        name: str,
        value: dict,
        indent_level: int,
    ):
        """
        Maps will be implemented when Message.format() will be refactored
        """
        indent = self._format_indent * indent_level
        buffer.append(f'{indent}{name} = {value}')

    def _format_bytes(
        self,
        buffer: list,
        name: str,
        value: bytes,
        indent_level: int,
    ):
        indent = self._format_indent * indent_level
        first_n_elements = 15

        if len(value) > first_n_elements:
            value_display = f"{value[:first_n_elements]} ... {len(value) - first_n_elements:_} bytes more"
        else:
            value_display = value

        buffer.append(f'{indent}{name + " =" if name else ""} {value_display}')

    def _format_string(
        self,
        buffer: list,
        name: str,
        value: str,
        indent_level: int,
    ):
        indent = self._format_indent * indent_level
        first_n_elements = 50

        if len(value) > first_n_elements:
            value_display = f"{value[:first_n_elements]!r} ... {len(value) - first_n_elements:_} characters more"
        else:
            value_display = repr(value)

        buffer.append(f'{indent}{name + " =" if name else ""} {value_display}')

    def _format_value(self, name: str, value, buffer: list, indent_level: int):
        type_to_formatter = {
            ValidatedList: self._format_repeated,
            ValidatedDict: self._format_map,
            bytes: self._format_bytes,
            str: self._format_string,
        }
        formatter = None

        if isinstance(value, Message):
            formatter = self._format_nested_message
        elif isinstance(value, IntEnum):
            formatter = self._format_enum
        elif type(value) in type_to_formatter:
            formatter = type_to_formatter[type(value)]

        if formatter:
            formatter(
                buffer,
                name,
                value,
                indent_level,
            )
        else:
            indent = self._format_indent * indent_level
            buffer.append(f'{indent}{name + " = " if name else ""}{value!r}')

    # The following methods provided for libraries like grpclib to simplify end-user experience
    def SerializeToString(self):
        return self.to_bytes()

    @classmethod
    def FromString(cls, data):
        return cls.from_bytes(data)
