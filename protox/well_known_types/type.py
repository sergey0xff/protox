from enum import IntEnum

from typing import List, Optional

import protox
from protox import Message, fields
from protox.well_known_types.any import Any
from protox.well_known_types.source_context import SourceContext


class Syntax(IntEnum):
    SYNTAX_PROTO2 = 0
    SYNTAX_PROTO3 = 1


class Option(Message):
    name: Optional[str] = fields.String(number=1)
    value: Optional[Any] = Any.as_field(number=2)

    def __init__(
        self,
        *,
        name: str = None,
        value: Any = None,
    ):
        super().__init__(
            name=name,
            value=value,
        )


class EnumValue(Message):
    name: Optional[str] = fields.String(number=1)
    number: Optional[int] = fields.Int32(number=2)
    options: List[Option] = Option.as_repeated(number=3)

    def __init__(
        self,
        *,
        name: str = None,
        number: int = None,
        options: List[Option] = None,
    ):
        super().__init__(
            name=name,
            number=number,
            options=options,
        )


class Enum(Message):
    name: Optional[str] = fields.String(number=1)
    enumvalue: List[EnumValue] = EnumValue.as_repeated(number=2)
    options: List[Option] = Option.as_repeated(number=3)
    source_context: Optional[SourceContext] = SourceContext.as_field(number=4)
    syntax: Optional[Syntax] = fields.EnumField(Syntax, number=5)

    def __init__(
        self,
        *,
        name: str = None,
        enumvalue: List[EnumValue] = None,
        options: List[Option] = None,
        source_context: SourceContext = None,
        syntax: Syntax = None,
    ):
        super().__init__(
            name=name,
            enumvalue=enumvalue,
            options=options,
            source_context=source_context,
            syntax=syntax,
        )


class Field(Message):
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

    kind: Optional[Kind] = fields.EnumField(Kind, number=1)
    cardinality: Optional[Cardinality] = fields.EnumField(Cardinality, number=2)
    number: Optional[int] = fields.Int32(number=3)
    name: Optional[str] = fields.String(number=4)
    type_url: Optional[str] = fields.String(number=6)
    oneof_index: Optional[int] = fields.Int32(number=7)
    packed: Optional[int] = fields.Bool(number=8)
    options: List[Option] = Option.as_repeated(number=9)
    json_name: Optional[str] = fields.String(number=10)
    default_value: Optional[str] = fields.String(number=11)

    def __init__(
        self,
        *,
        kind: Kind = None,
        cardinality: Cardinality = None,
        number: int = None,
        name: str = None,
        type_url: str = None,
        oneof_index: int = None,
        packed: int = None,
        options: List[Option] = None,
        json_name: str = None,
        default_value: str = None,
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


class Type(Message):
    name: Optional[str] = protox.String(number=1)
    fields: List[Field] = Field.as_repeated(number=2)
    oneofs: List[str] = protox.String.as_repeated(number=3)
    options: List[Option] = Option.as_repeated(number=4)
    source_context: Optional[SourceContext] = SourceContext.as_field(number=5)
    syntax: Optional[Syntax] = protox.EnumField(Syntax, number=6)

    def __init__(
        self,
        *,
        name: str = None,
        fields: List[Field] = None,
        oneofs: List[str] = None,
        options: List[Option] = None,
        source_context: SourceContext = None,
        syntax: Syntax = None,
    ):
        super().__init__(
            name=name,
            fields=fields,
            oneofs=oneofs,
            options=options,
            source_context=source_context,
            syntax=syntax,
        )
