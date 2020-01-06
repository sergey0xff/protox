import io
from abc import ABCMeta
from enum import IntEnum
from typing import BinaryIO, Tuple, List, Callable, Optional, TypeVar, Type, Dict, Union

from protox.encoding import decode_header, wire_type_to_decoder
from protox.exceptions import MessageEncodeError, MessageDecodeError, FieldValidationError
from protox.fields import Field, OneOf, Repeated, MessageField, MapField
from protox.validated_dict import ValidatedDict
from protox.validated_list import ValidatedList


class FieldGetter:
    def __init__(self, key, default):
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
    """
    The following function was intentionally extracted from the Message type.
    The use case of the function is delayed fields assigning for cases like recursion
    and circular dependency when we first define a message before referencing it.
    """

    if isinstance(field, Repeated):
        field_getter = RepeatedGetter(name, field.field)
    elif isinstance(field, MapField):
        field_getter = MapGetter(name, field)
    else:
        field_getter = FieldGetter(name, field.default)

    if name in message_type._one_of_by_field_name:
        if field.required:
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
        new_cls: Type[Message] = super().__new__(
            mcs, name, bases, namespace
        )

        if name != 'Message':
            fields = mcs._collect_fields(name, namespace)

            new_cls._field_by_name = {}
            new_cls._field_by_number = {}

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

                if len(value.fields) < 2:
                    raise FieldValidationError(
                        f'one_f {key!r} of message {class_name!r} should have at least 2 fields'
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

                if value.default is not None:
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
    # The following fields are set by metaclass
    _field_by_name: Dict[str, Union[Field, Repeated]]
    _field_by_number: Dict[int, Union[Field, Repeated]]
    _one_of_by_field_name: dict

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
            required=required
        )

    @classmethod
    def as_repeated(cls, *, number: int) -> Repeated:
        return Repeated(
            cls,
            number=number
        )

    @classmethod
    def from_bytes(cls: Type[T], data: bytes) -> T:
        if not data:
            return cls()

        stream = io.BytesIO(data)
        return cls.from_stream(stream)

    @classmethod
    def from_stream(cls: Type[T], stream: BinaryIO) -> T:
        """
        FIXME: Probably  Replace message_fields with creating a new Message instance
         and setting attributes on it
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
                    # FIXME: probably extract the following fields to message_fields = {}
                    message_fields.setdefault(field.name, [])
                    message_fields[field.name].append(field.decode(stream))
                elif isinstance(field, MapField):
                    message_fields.setdefault(field.name, {})
                    key, value = field.decode(stream)
                    message_fields[field.name][key] = value
                else:
                    message_fields[field.name] = field.decode(stream)
            else:
                # read and discard unknown field
                wire_type_to_decoder[wire_type](stream)

        for key, field, in cls._field_by_name.items():
            if field.required and not field.default and key not in message_fields:
                raise MessageDecodeError(
                    f"Field {cls.__name__}.{key} is required but was not read from input stream"
                )

        return cls(**message_fields)

    def to_bytes(self) -> bytes:
        stream = io.BytesIO()
        self.to_stream(stream)
        stream.seek(0)
        return stream.read()

    def to_stream(self, stream: BinaryIO):
        for key, field in self._field_by_name.items():
            value = getattr(self, key)

            if value is None:
                if field.required:
                    raise MessageEncodeError(
                        f'Field {type(self).__name__}.{key} is required but not set'
                    )
                else:
                    continue

            stream.write(field.encode(value))

    def has_field(self, name: str) -> bool:
        """
        has_field checks if field was explicitly set

        :raises:
            AttributeError: if message has no such field
        """
        if name not in self._field_by_name:
            raise AttributeError(
                f"Protocol message {type(self).__qualname__} has no such field {name!r}"
            )

        return super().__getattribute__(name) is not None

    def which_one_of(self, one_of_name: str) -> Optional[str]:
        if one_of_name not in self._one_ofs:
            raise ValueError(
                f'Protocol message {type(self).__qualname__} has no one_of {one_of_name!r}'
            )

        try:
            return self._which_one_of[one_of_name]
        except KeyError:
            return None

    def empty(self) -> bool:
        return not bool(self._data)

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

    def __str__(self):
        return self.format()

    def format(self, buffer: list = None, indent_level=0, indent='  ') -> str:
        buffer = buffer or []

        if indent_level == 0:
            buffer.append(f"{type(self).__name__}")

        indent_level += 1

        for key, value in self._data.items():
            self._format(key, value, buffer, indent_level, indent)

        return '\n'.join(buffer)

    def _format(self, field_name, value, buffer: list, indent_level, indent):
        # FIXME: refactor _format
        #  write a _format_...() function for each case
        local_indent = indent * indent_level

        if isinstance(value, Message):
            buffer.append(f'{local_indent}{field_name}: {type(value).__name__} = {{')
            value.format(buffer, indent_level, indent)
            buffer.append(f'{local_indent}}}')
        elif isinstance(value, IntEnum):
            buffer.append(f'{local_indent}{field_name + " =" if field_name else ""} {str(value)}[{value.value}]')
        elif isinstance(value, ValidatedList):
            buffer.append(f'{local_indent}{field_name}: {self._field_by_name[field_name].of_type.__name__} = [')
            nested_indent = local_indent + indent

            for item in value:
                if isinstance(item, Message):
                    if item.empty():
                        buffer.append(f'{nested_indent}{{}}')
                    else:
                        buffer.append(f'{nested_indent}{{')
                        item.format(buffer, indent_level + 1)
                        buffer.append(f'{nested_indent}}}')
                else:
                    self._format('', item, buffer, indent_level + 1, indent)

            buffer.append(f'{local_indent}]')
        elif isinstance(value, bytes):
            first_n_elements = 15

            if len(value) > first_n_elements:
                value_display = f"{value[:first_n_elements]} ... {len(value) - first_n_elements:_} bytes more"
            else:
                value_display = value

            buffer.append(f'{local_indent}{field_name + " =" if field_name else ""} {value_display}')
        elif isinstance(value, str):
            first_n_elements = 50

            if len(value) > first_n_elements:
                value_display = f"{value[:first_n_elements]!r} ... {len(value) - first_n_elements:_} characters more"
            else:
                value_display = repr(value)

            buffer.append(f'{local_indent}{field_name + " =" if field_name else ""} {value_display}')
        else:
            buffer.append(f'{local_indent}{field_name + " =" if field_name else ""} {value!r}')
