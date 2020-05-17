import typing
from enum import IntEnum

import protox
from protox.well_known_types.any import Any
from protox.well_known_types.source_context import SourceContext


class Syntax(IntEnum):
    SYNTAX_PROTO2 = 0
    SYNTAX_PROTO3 = 1


class Type(protox.Message):
    name: typing.Optional[str]
    fields: typing.List['Field']
    oneofs: typing.List[str]
    options: typing.List['Option']
    source_context: typing.Optional[SourceContext]
    syntax: typing.Optional[Syntax]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        fields: typing.List['Field'] = None,
        oneofs: typing.List[str] = None,
        options: typing.List['Option'] = None,
        source_context: typing.Optional[SourceContext] = None,
        syntax: typing.Optional[Syntax] = None,
    ):
        super().__init__(
            name=name,
            fields=fields,
            oneofs=oneofs,
            options=options,
            source_context=source_context,
            syntax=syntax,
        )


class Field(protox.Message):
    class Kind(IntEnum):
        TYPE_UNKNOWN = 0
        TYPE_DOUBLE = 1
        TYPE_FLOAT = 2
        TYPE_INT64 = 3
        TYPE_UINT64 = 4
        TYPE_INT32 = 5
        TYPE_FIXED64 = 6
        TYPE_FIXED32 = 7
        TYPE_BOOL = 8
        TYPE_STRING = 9
        TYPE_GROUP = 10
        TYPE_MESSAGE = 11
        TYPE_BYTES = 12
        TYPE_UINT32 = 13
        TYPE_ENUM = 14
        TYPE_SFIXED32 = 15
        TYPE_SFIXED64 = 16
        TYPE_SINT32 = 17
        TYPE_SINT64 = 18

    class Cardinality(IntEnum):
        CARDINALITY_UNKNOWN = 0
        CARDINALITY_OPTIONAL = 1
        CARDINALITY_REQUIRED = 2
        CARDINALITY_REPEATED = 3

    kind: typing.Optional['Field.Kind']
    cardinality: typing.Optional['Field.Cardinality']
    number: typing.Optional[int]
    name: typing.Optional[str]
    type_url: typing.Optional[str]
    oneof_index: typing.Optional[int]
    packed: typing.Optional[bool]
    options: typing.List['Option']
    json_name: typing.Optional[str]
    default_value: typing.Optional[str]

    def __init__(
        self,
        *,
        kind: typing.Optional['Field.Kind'] = None,
        cardinality: typing.Optional['Field.Cardinality'] = None,
        number: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        type_url: typing.Optional[str] = None,
        oneof_index: typing.Optional[int] = None,
        packed: typing.Optional[bool] = None,
        options: typing.List['Option'] = None,
        json_name: typing.Optional[str] = None,
        default_value: typing.Optional[str] = None,
    ):
        super().__init__(
            kind=kind,
            cardinality=cardinality,
            number=number,
            name=name,
            type_url=type_url,
            oneof_index=oneof_index,
            packed=packed,
            options=options,
            json_name=json_name,
            default_value=default_value,
        )


class Enum(protox.Message):
    name: typing.Optional[str]
    enumvalue: typing.List['EnumValue']
    options: typing.List['Option']
    source_context: typing.Optional[SourceContext]
    syntax: typing.Optional[Syntax]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        enumvalue: typing.List['EnumValue'] = None,
        options: typing.List['Option'] = None,
        source_context: typing.Optional[SourceContext] = None,
        syntax: typing.Optional[Syntax] = None,
    ):
        super().__init__(
            name=name,
            enumvalue=enumvalue,
            options=options,
            source_context=source_context,
            syntax=syntax,
        )


class EnumValue(protox.Message):
    name: typing.Optional[str]
    number: typing.Optional[int]
    options: typing.List['Option']

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        number: typing.Optional[int] = None,
        options: typing.List['Option'] = None,
    ):
        super().__init__(
            name=name,
            number=number,
            options=options,
        )


class Option(protox.Message):
    name: typing.Optional[str]
    value: typing.Optional[Any]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        value: typing.Optional[Any] = None,
    ):
        super().__init__(
            name=name,
            value=value,
        )


protox.define_fields(
    Type,
    name=protox.String(
        number=1, required=False
    ),
    fields=Field.as_repeated(
        number=2
    ),
    oneofs=protox.String.as_repeated(
        number=3
    ),
    options=Option.as_repeated(
        number=4
    ),
    source_context=SourceContext.as_field(
        number=5,
    ),
    syntax=protox.EnumField(
        number=6, py_enum=Syntax, required=False
    ),
)

protox.define_fields(
    Field,
    kind=protox.EnumField(
        number=1, py_enum=Field.Kind, required=False
    ),
    cardinality=protox.EnumField(
        number=2, py_enum=Field.Cardinality, required=False
    ),
    number=protox.Int32(
        number=3, required=False
    ),
    name=protox.String(
        number=4, required=False
    ),
    type_url=protox.String(
        number=6, required=False
    ),
    oneof_index=protox.Int32(
        number=7, required=False
    ),
    packed=protox.Bool(
        number=8, required=False
    ),
    options=Option.as_repeated(
        number=9
    ),
    json_name=protox.String(
        number=10, required=False
    ),
    default_value=protox.String(
        number=11, required=False
    ),
)

protox.define_fields(
    Enum,
    name=protox.String(
        number=1, required=False
    ),
    enumvalue=EnumValue.as_repeated(
        number=2
    ),
    options=Option.as_repeated(
        number=3
    ),
    source_context=SourceContext.as_field(
        number=4
    ),
    syntax=protox.EnumField(
        number=5, py_enum=Syntax, required=False
    ),
)

protox.define_fields(
    EnumValue,
    name=protox.String(
        number=1, required=False
    ),
    number=protox.Int32(
        number=2, required=False
    ),
    options=Option.as_repeated(
        number=3
    ),
)

protox.define_fields(
    Option,
    name=protox.String(
        number=1, required=False
    ),
    value=Any.as_field(
        number=2
    ),
)
