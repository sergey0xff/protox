import typing
from enum import IntEnum

import protox


class FileDescriptorSet(protox.Message):
    file: typing.List['FileDescriptorProto']

    def __init__(
        self,
        *,
        file: typing.List['FileDescriptorProto'] = None,
    ):
        super().__init__(
            file=file,
        )


class FileDescriptorProto(protox.Message):
    name: typing.Optional[str]
    package: typing.Optional[str]
    dependency: typing.List[str]
    public_dependency: typing.List[int]
    weak_dependency: typing.List[int]
    message_type: typing.List['DescriptorProto']
    enum_type: typing.List['EnumDescriptorProto']
    service: typing.List['ServiceDescriptorProto']
    extension: typing.List['FieldDescriptorProto']
    options: typing.Optional['FileOptions']
    source_code_info: typing.Optional['SourceCodeInfo']
    syntax: typing.Optional[str]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        package: typing.Optional[str] = None,
        dependency: typing.List[str] = None,
        public_dependency: typing.List[int] = None,
        weak_dependency: typing.List[int] = None,
        message_type: typing.List['DescriptorProto'] = None,
        enum_type: typing.List['EnumDescriptorProto'] = None,
        service: typing.List['ServiceDescriptorProto'] = None,
        extension: typing.List['FieldDescriptorProto'] = None,
        options: typing.Optional['FileOptions'] = None,
        source_code_info: typing.Optional['SourceCodeInfo'] = None,
        syntax: typing.Optional[str] = None,
    ):
        super().__init__(
            name=name,
            package=package,
            dependency=dependency,
            public_dependency=public_dependency,
            weak_dependency=weak_dependency,
            message_type=message_type,
            enum_type=enum_type,
            service=service,
            extension=extension,
            options=options,
            source_code_info=source_code_info,
            syntax=syntax,
        )


class DescriptorProto(protox.Message):
    class ExtensionRange(protox.Message):
        start: typing.Optional[int]
        end: typing.Optional[int]
        options: typing.Optional['ExtensionRangeOptions']

        def __init__(
            self,
            *,
            start: typing.Optional[int] = None,
            end: typing.Optional[int] = None,
            options: typing.Optional['ExtensionRangeOptions'] = None,
        ):
            super().__init__(
                start=start,
                end=end,
                options=options,
            )

    class ReservedRange(protox.Message):
        start: typing.Optional[int]
        end: typing.Optional[int]

        def __init__(
            self,
            *,
            start: typing.Optional[int] = None,
            end: typing.Optional[int] = None,
        ):
            super().__init__(
                start=start,
                end=end,
            )

    name: typing.Optional[str]
    field: typing.List['FieldDescriptorProto']
    extension: typing.List['FieldDescriptorProto']
    nested_type: typing.List['DescriptorProto']
    enum_type: typing.List['EnumDescriptorProto']
    extension_range: typing.List['DescriptorProto.ExtensionRange']
    oneof_decl: typing.List['OneofDescriptorProto']
    options: typing.Optional['MessageOptions']
    reserved_range: typing.List['DescriptorProto.ReservedRange']
    reserved_name: typing.List[str]

    # The following fields provided by code generator
    full_name: typing.Optional[str] = None
    file_descriptor: FileDescriptorProto = None

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        field: typing.List['FieldDescriptorProto'] = None,
        extension: typing.List['FieldDescriptorProto'] = None,
        nested_type: typing.List['DescriptorProto'] = None,
        enum_type: typing.List['EnumDescriptorProto'] = None,
        extension_range: typing.List['DescriptorProto.ExtensionRange'] = None,
        oneof_decl: typing.List['OneofDescriptorProto'] = None,
        options: typing.Optional['MessageOptions'] = None,
        reserved_range: typing.List['DescriptorProto.ReservedRange'] = None,
        reserved_name: typing.List[str] = None,
    ):
        super().__init__(
            name=name,
            field=field,
            extension=extension,
            nested_type=nested_type,
            enum_type=enum_type,
            extension_range=extension_range,
            oneof_decl=oneof_decl,
            options=options,
            reserved_range=reserved_range,
            reserved_name=reserved_name,
        )


class ExtensionRangeOptions(protox.Message):
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            uninterpreted_option=uninterpreted_option,
        )


class FieldDescriptorProto(protox.Message):
    class Type(IntEnum):
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

    class Label(IntEnum):
        LABEL_OPTIONAL = 1
        LABEL_REQUIRED = 2
        LABEL_REPEATED = 3

    name: typing.Optional[str]
    number: typing.Optional[int]
    label: typing.Optional['FieldDescriptorProto.Label']
    type: typing.Optional['FieldDescriptorProto.Type']
    type_name: typing.Optional[str]
    extendee: typing.Optional[str]
    default_value: typing.Optional[str]
    oneof_index: typing.Optional[int]
    json_name: typing.Optional[str]
    options: typing.Optional['FieldOptions']

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        number: typing.Optional[int] = None,
        label: typing.Optional['FieldDescriptorProto.Label'] = None,
        type: typing.Optional['FieldDescriptorProto.Type'] = None,
        type_name: typing.Optional[str] = None,
        extendee: typing.Optional[str] = None,
        default_value: typing.Optional[str] = None,
        oneof_index: typing.Optional[int] = None,
        json_name: typing.Optional[str] = None,
        options: typing.Optional['FieldOptions'] = None,
    ):
        super().__init__(
            name=name,
            number=number,
            label=label,
            type=type,
            type_name=type_name,
            extendee=extendee,
            default_value=default_value,
            oneof_index=oneof_index,
            json_name=json_name,
            options=options,
        )


class OneofDescriptorProto(protox.Message):
    name: typing.Optional[str]
    options: typing.Optional['OneofOptions']

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        options: typing.Optional['OneofOptions'] = None,
    ):
        super().__init__(
            name=name,
            options=options,
        )


class EnumDescriptorProto(protox.Message):
    class EnumReservedRange(protox.Message):
        start: typing.Optional[int]
        end: typing.Optional[int]

        def __init__(
            self,
            *,
            start: typing.Optional[int] = None,
            end: typing.Optional[int] = None,
        ):
            super().__init__(
                start=start,
                end=end,
            )

    name: typing.Optional[str]
    value: typing.List['EnumValueDescriptorProto']
    options: typing.Optional['EnumOptions']
    reserved_range: typing.List['EnumDescriptorProto.EnumReservedRange']
    reserved_name: typing.List[str]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        value: typing.List['EnumValueDescriptorProto'] = None,
        options: typing.Optional['EnumOptions'] = None,
        reserved_range: typing.List['EnumDescriptorProto.EnumReservedRange'] = None,
        reserved_name: typing.List[str] = None,
    ):
        super().__init__(
            name=name,
            value=value,
            options=options,
            reserved_range=reserved_range,
            reserved_name=reserved_name,
        )


class EnumValueDescriptorProto(protox.Message):
    name: typing.Optional[str]
    number: typing.Optional[int]
    options: typing.Optional['EnumValueOptions']

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        number: typing.Optional[int] = None,
        options: typing.Optional['EnumValueOptions'] = None,
    ):
        super().__init__(
            name=name,
            number=number,
            options=options,
        )


class ServiceDescriptorProto(protox.Message):
    name: typing.Optional[str]
    method: typing.List['MethodDescriptorProto']
    options: typing.Optional['ServiceOptions']

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        method: typing.List['MethodDescriptorProto'] = None,
        options: typing.Optional['ServiceOptions'] = None,
    ):
        super().__init__(
            name=name,
            method=method,
            options=options,
        )


class MethodDescriptorProto(protox.Message):
    name: typing.Optional[str]
    input_type: typing.Optional[str]
    output_type: typing.Optional[str]
    options: typing.Optional['MethodOptions']
    client_streaming: typing.Optional[bool]
    server_streaming: typing.Optional[bool]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        input_type: typing.Optional[str] = None,
        output_type: typing.Optional[str] = None,
        options: typing.Optional['MethodOptions'] = None,
        client_streaming: typing.Optional[bool] = None,
        server_streaming: typing.Optional[bool] = None,
    ):
        super().__init__(
            name=name,
            input_type=input_type,
            output_type=output_type,
            options=options,
            client_streaming=client_streaming,
            server_streaming=server_streaming,
        )


class FileOptions(protox.Message):
    class OptimizeMode(IntEnum):
        SPEED = 1
        CODE_SIZE = 2
        LITE_RUNTIME = 3

    java_package: typing.Optional[str]
    java_outer_classname: typing.Optional[str]
    java_multiple_files: typing.Optional[bool]
    java_generate_equals_and_hash: typing.Optional[bool]
    java_string_check_utf8: typing.Optional[bool]
    optimize_for: typing.Optional['FileOptions.OptimizeMode']
    go_package: typing.Optional[str]
    cc_generic_services: typing.Optional[bool]
    java_generic_services: typing.Optional[bool]
    py_generic_services: typing.Optional[bool]
    php_generic_services: typing.Optional[bool]
    deprecated: typing.Optional[bool]
    cc_enable_arenas: typing.Optional[bool]
    objc_class_prefix: typing.Optional[str]
    csharp_namespace: typing.Optional[str]
    swift_prefix: typing.Optional[str]
    php_class_prefix: typing.Optional[str]
    php_namespace: typing.Optional[str]
    php_metadata_namespace: typing.Optional[str]
    ruby_package: typing.Optional[str]
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        java_package: typing.Optional[str] = None,
        java_outer_classname: typing.Optional[str] = None,
        java_multiple_files: typing.Optional[bool] = None,
        java_generate_equals_and_hash: typing.Optional[bool] = None,
        java_string_check_utf8: typing.Optional[bool] = None,
        optimize_for: typing.Optional['FileOptions.OptimizeMode'] = None,
        go_package: typing.Optional[str] = None,
        cc_generic_services: typing.Optional[bool] = None,
        java_generic_services: typing.Optional[bool] = None,
        py_generic_services: typing.Optional[bool] = None,
        php_generic_services: typing.Optional[bool] = None,
        deprecated: typing.Optional[bool] = None,
        cc_enable_arenas: typing.Optional[bool] = None,
        objc_class_prefix: typing.Optional[str] = None,
        csharp_namespace: typing.Optional[str] = None,
        swift_prefix: typing.Optional[str] = None,
        php_class_prefix: typing.Optional[str] = None,
        php_namespace: typing.Optional[str] = None,
        php_metadata_namespace: typing.Optional[str] = None,
        ruby_package: typing.Optional[str] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            java_package=java_package,
            java_outer_classname=java_outer_classname,
            java_multiple_files=java_multiple_files,
            java_generate_equals_and_hash=java_generate_equals_and_hash,
            java_string_check_utf8=java_string_check_utf8,
            optimize_for=optimize_for,
            go_package=go_package,
            cc_generic_services=cc_generic_services,
            java_generic_services=java_generic_services,
            py_generic_services=py_generic_services,
            php_generic_services=php_generic_services,
            deprecated=deprecated,
            cc_enable_arenas=cc_enable_arenas,
            objc_class_prefix=objc_class_prefix,
            csharp_namespace=csharp_namespace,
            swift_prefix=swift_prefix,
            php_class_prefix=php_class_prefix,
            php_namespace=php_namespace,
            php_metadata_namespace=php_metadata_namespace,
            ruby_package=ruby_package,
            uninterpreted_option=uninterpreted_option,
        )


class MessageOptions(protox.Message):
    message_set_wire_format: typing.Optional[bool]
    no_standard_descriptor_accessor: typing.Optional[bool]
    deprecated: typing.Optional[bool]
    map_entry: typing.Optional[bool]
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        message_set_wire_format: typing.Optional[bool] = None,
        no_standard_descriptor_accessor: typing.Optional[bool] = None,
        deprecated: typing.Optional[bool] = None,
        map_entry: typing.Optional[bool] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            message_set_wire_format=message_set_wire_format,
            no_standard_descriptor_accessor=no_standard_descriptor_accessor,
            deprecated=deprecated,
            map_entry=map_entry,
            uninterpreted_option=uninterpreted_option,
        )


class FieldOptions(protox.Message):
    class CType(IntEnum):
        STRING = 0
        CORD = 1
        STRING_PIECE = 2

    class JSType(IntEnum):
        JS_NORMAL = 0
        JS_STRING = 1
        JS_NUMBER = 2

    ctype: typing.Optional['FieldOptions.CType']
    packed: typing.Optional[bool]
    jstype: typing.Optional['FieldOptions.JSType']
    lazy: typing.Optional[bool]
    deprecated: typing.Optional[bool]
    weak: typing.Optional[bool]
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        ctype: typing.Optional['FieldOptions.CType'] = None,
        packed: typing.Optional[bool] = None,
        jstype: typing.Optional['FieldOptions.JSType'] = None,
        lazy: typing.Optional[bool] = None,
        deprecated: typing.Optional[bool] = None,
        weak: typing.Optional[bool] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            ctype=ctype,
            packed=packed,
            jstype=jstype,
            lazy=lazy,
            deprecated=deprecated,
            weak=weak,
            uninterpreted_option=uninterpreted_option,
        )


class OneofOptions(protox.Message):
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            uninterpreted_option=uninterpreted_option,
        )


class EnumOptions(protox.Message):
    allow_alias: typing.Optional[bool]
    deprecated: typing.Optional[bool]
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        allow_alias: typing.Optional[bool] = None,
        deprecated: typing.Optional[bool] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            allow_alias=allow_alias,
            deprecated=deprecated,
            uninterpreted_option=uninterpreted_option,
        )


class EnumValueOptions(protox.Message):
    deprecated: typing.Optional[bool]
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        deprecated: typing.Optional[bool] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            deprecated=deprecated,
            uninterpreted_option=uninterpreted_option,
        )


class ServiceOptions(protox.Message):
    deprecated: typing.Optional[bool]
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        deprecated: typing.Optional[bool] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            deprecated=deprecated,
            uninterpreted_option=uninterpreted_option,
        )


class MethodOptions(protox.Message):
    class IdempotencyLevel(IntEnum):
        IDEMPOTENCY_UNKNOWN = 0
        NO_SIDE_EFFECTS = 1
        IDEMPOTENT = 2

    deprecated: typing.Optional[bool]
    idempotency_level: typing.Optional['MethodOptions.IdempotencyLevel']
    uninterpreted_option: typing.List['UninterpretedOption']

    def __init__(
        self,
        *,
        deprecated: typing.Optional[bool] = None,
        idempotency_level: typing.Optional['MethodOptions.IdempotencyLevel'] = None,
        uninterpreted_option: typing.List['UninterpretedOption'] = None,
    ):
        super().__init__(
            deprecated=deprecated,
            idempotency_level=idempotency_level,
            uninterpreted_option=uninterpreted_option,
        )


class UninterpretedOption(protox.Message):
    class NamePart(protox.Message):
        name_part: str
        is_extension: bool

        def __init__(
            self,
            *,
            name_part: str = None,
            is_extension: bool = None,
        ):
            super().__init__(
                name_part=name_part,
                is_extension=is_extension,
            )

    name: typing.List['UninterpretedOption.NamePart']
    identifier_value: typing.Optional[str]
    positive_int_value: typing.Optional[int]
    negative_int_value: typing.Optional[int]
    double_value: typing.Optional[float]
    string_value: typing.Optional[bytes]
    aggregate_value: typing.Optional[str]

    def __init__(
        self,
        *,
        name: typing.List['UninterpretedOption.NamePart'] = None,
        identifier_value: typing.Optional[str] = None,
        positive_int_value: typing.Optional[int] = None,
        negative_int_value: typing.Optional[int] = None,
        double_value: typing.Optional[float] = None,
        string_value: typing.Optional[bytes] = None,
        aggregate_value: typing.Optional[str] = None,
    ):
        super().__init__(
            name=name,
            identifier_value=identifier_value,
            positive_int_value=positive_int_value,
            negative_int_value=negative_int_value,
            double_value=double_value,
            string_value=string_value,
            aggregate_value=aggregate_value,
        )


class SourceCodeInfo(protox.Message):
    class Location(protox.Message):
        path: typing.List[int]
        span: typing.List[int]
        leading_comments: typing.Optional[str]
        trailing_comments: typing.Optional[str]
        leading_detached_comments: typing.List[str]

        def __init__(
            self,
            *,
            path: typing.List[int] = None,
            span: typing.List[int] = None,
            leading_comments: typing.Optional[str] = None,
            trailing_comments: typing.Optional[str] = None,
            leading_detached_comments: typing.List[str] = None,
        ):
            super().__init__(
                path=path,
                span=span,
                leading_comments=leading_comments,
                trailing_comments=trailing_comments,
                leading_detached_comments=leading_detached_comments,
            )

    location: typing.List['SourceCodeInfo.Location']

    def __init__(
        self,
        *,
        location: typing.List['SourceCodeInfo.Location'] = None,
    ):
        super().__init__(
            location=location,
        )


class GeneratedCodeInfo(protox.Message):
    class Annotation(protox.Message):
        path: typing.List[int]
        source_file: typing.Optional[str]
        begin: typing.Optional[int]
        end: typing.Optional[int]

        def __init__(
            self,
            *,
            path: typing.List[int] = None,
            source_file: typing.Optional[str] = None,
            begin: typing.Optional[int] = None,
            end: typing.Optional[int] = None,
        ):
            super().__init__(
                path=path,
                source_file=source_file,
                begin=begin,
                end=end,
            )

    annotation: typing.List['GeneratedCodeInfo.Annotation']

    def __init__(
        self,
        *,
        annotation: typing.List['GeneratedCodeInfo.Annotation'] = None,
    ):
        super().__init__(
            annotation=annotation,
        )


protox.define_fields(
    FileDescriptorSet,
    file=FileDescriptorProto.as_repeated(
        number=1
    ),
)

protox.define_fields(
    FileDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    package=protox.String(
        number=2, required=False
    ),
    dependency=protox.String.as_repeated(
        number=3
    ),
    public_dependency=protox.Int32.as_repeated(
        number=10
    ),
    weak_dependency=protox.Int32.as_repeated(
        number=11
    ),
    message_type=DescriptorProto.as_repeated(
        number=4
    ),
    enum_type=EnumDescriptorProto.as_repeated(
        number=5
    ),
    service=ServiceDescriptorProto.as_repeated(
        number=6
    ),
    extension=FieldDescriptorProto.as_repeated(
        number=7
    ),
    options=FileOptions.as_field(
        number=8
    ),
    source_code_info=SourceCodeInfo.as_field(
        number=9
    ),
    syntax=protox.String(
        number=12, required=False
    ),
)

protox.define_fields(
    DescriptorProto.ExtensionRange,
    start=protox.Int32(
        number=1, required=False
    ),
    end=protox.Int32(
        number=2, required=False
    ),
    options=ExtensionRangeOptions.as_field(
        number=3
    ),
)

protox.define_fields(
    DescriptorProto.ReservedRange,
    start=protox.Int32(
        number=1, required=False
    ),
    end=protox.Int32(
        number=2, required=False
    ),
)

protox.define_fields(
    DescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    field=FieldDescriptorProto.as_repeated(
        number=2
    ),
    extension=FieldDescriptorProto.as_repeated(
        number=6
    ),
    nested_type=DescriptorProto.as_repeated(
        number=3
    ),
    enum_type=EnumDescriptorProto.as_repeated(
        number=4
    ),
    extension_range=DescriptorProto.ExtensionRange.as_repeated(
        number=5
    ),
    oneof_decl=OneofDescriptorProto.as_repeated(
        number=8
    ),
    options=MessageOptions.as_field(
        number=7
    ),
    reserved_range=DescriptorProto.ReservedRange.as_repeated(
        number=9
    ),
    reserved_name=protox.String.as_repeated(
        number=10
    ),
)

protox.define_fields(
    ExtensionRangeOptions,
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    FieldDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    number=protox.Int32(
        number=3, required=False
    ),
    label=protox.EnumField(
        number=4, py_enum=FieldDescriptorProto.Label, required=False
    ),
    type=protox.EnumField(
        number=5, py_enum=FieldDescriptorProto.Type, required=False
    ),
    type_name=protox.String(
        number=6, required=False
    ),
    extendee=protox.String(
        number=2, required=False
    ),
    default_value=protox.String(
        number=7, required=False
    ),
    oneof_index=protox.Int32(
        number=9, required=False
    ),
    json_name=protox.String(
        number=10, required=False
    ),
    options=FieldOptions.as_field(
        number=8
    ),
)

protox.define_fields(
    OneofDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    options=OneofOptions.as_field(
        number=2
    ),
)

protox.define_fields(
    EnumDescriptorProto.EnumReservedRange,
    start=protox.Int32(
        number=1
    ),
    end=protox.Int32(
        number=2
    ),
)

protox.define_fields(
    EnumDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    value=EnumValueDescriptorProto.as_repeated(
        number=2
    ),
    options=EnumOptions.as_field(
        number=3
    ),
    reserved_range=EnumDescriptorProto.EnumReservedRange.as_repeated(
        number=4
    ),
    reserved_name=protox.String.as_repeated(
        number=5
    ),
)

protox.define_fields(
    EnumValueDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    number=protox.Int32(
        number=2, required=False
    ),
    options=EnumValueOptions.as_field(
        number=3
    ),
)

protox.define_fields(
    ServiceDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    method=MethodDescriptorProto.as_repeated(
        number=2
    ),
    options=ServiceOptions.as_field(
        number=3
    ),
)

protox.define_fields(
    MethodDescriptorProto,
    name=protox.String(
        number=1, required=False
    ),
    input_type=protox.String(
        number=2, required=False
    ),
    output_type=protox.String(
        number=3, required=False
    ),
    options=MethodOptions.as_field(
        number=4
    ),
    client_streaming=protox.Bool(
        number=5, default=False, required=False
    ),
    server_streaming=protox.Bool(
        number=6, default=False, required=False
    ),
)

protox.define_fields(
    FileOptions,
    java_package=protox.String(
        number=1, required=False
    ),
    java_outer_classname=protox.String(
        number=8, required=False
    ),
    java_multiple_files=protox.Bool(
        number=10, default=False, required=False
    ),
    java_generate_equals_and_hash=protox.Bool(
        number=20, required=False
    ),
    java_string_check_utf8=protox.Bool(
        number=27, default=False, required=False
    ),
    optimize_for=protox.EnumField(
        number=9, py_enum=FileOptions.OptimizeMode, default=FileOptions.OptimizeMode.SPEED, required=False
    ),
    go_package=protox.String(
        number=11, required=False
    ),
    cc_generic_services=protox.Bool(
        number=16, default=False, required=False
    ),
    java_generic_services=protox.Bool(
        number=17, default=False, required=False
    ),
    py_generic_services=protox.Bool(
        number=18, default=False, required=False
    ),
    php_generic_services=protox.Bool(
        number=42, default=False, required=False
    ),
    deprecated=protox.Bool(
        number=23, default=False, required=False
    ),
    cc_enable_arenas=protox.Bool(
        number=31, default=False, required=False
    ),
    objc_class_prefix=protox.String(
        number=36, required=False
    ),
    csharp_namespace=protox.String(
        number=37, required=False
    ),
    swift_prefix=protox.String(
        number=39, required=False
    ),
    php_class_prefix=protox.String(
        number=40, required=False
    ),
    php_namespace=protox.String(
        number=41, required=False
    ),
    php_metadata_namespace=protox.String(
        number=44, required=False
    ),
    ruby_package=protox.String(
        number=45, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    MessageOptions,
    message_set_wire_format=protox.Bool(
        number=1, default=False, required=False
    ),
    no_standard_descriptor_accessor=protox.Bool(
        number=2, default=False, required=False
    ),
    deprecated=protox.Bool(
        number=3, default=False, required=False
    ),
    map_entry=protox.Bool(
        number=7, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    FieldOptions,
    ctype=protox.EnumField(
        number=1, py_enum=FieldOptions.CType, default=FieldOptions.CType.STRING, required=False
    ),
    packed=protox.Bool(
        number=2, required=False
    ),
    jstype=protox.EnumField(
        number=6, py_enum=FieldOptions.JSType, default=FieldOptions.JSType.JS_NORMAL, required=False
    ),
    lazy=protox.Bool(
        number=5, default=False, required=False
    ),
    deprecated=protox.Bool(
        number=3, default=False, required=False
    ),
    weak=protox.Bool(
        number=10, default=False, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    OneofOptions,
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    EnumOptions,
    allow_alias=protox.Bool(
        number=2, required=False
    ),
    deprecated=protox.Bool(
        number=3, default=False, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    EnumValueOptions,
    deprecated=protox.Bool(
        number=1, default=False, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    ServiceOptions,
    deprecated=protox.Bool(
        number=33, default=False, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    MethodOptions,
    deprecated=protox.Bool(
        number=33, default=False, required=False
    ),
    idempotency_level=protox.EnumField(
        number=34, py_enum=MethodOptions.IdempotencyLevel, default=MethodOptions.IdempotencyLevel.IDEMPOTENCY_UNKNOWN, required=False
    ),
    uninterpreted_option=UninterpretedOption.as_repeated(
        number=999
    ),
)

protox.define_fields(
    UninterpretedOption.NamePart,
    name_part=protox.String(
        number=1, required=True
    ),
    is_extension=protox.Bool(
        number=2, required=True
    ),
)

protox.define_fields(
    UninterpretedOption,
    name=UninterpretedOption.NamePart.as_repeated(
        number=2
    ),
    identifier_value=protox.String(
        number=3, required=False
    ),
    positive_int_value=protox.UInt64(
        number=4, required=False
    ),
    negative_int_value=protox.Int64(
        number=5, required=False
    ),
    double_value=protox.Double(
        number=6, required=False
    ),
    string_value=protox.Bytes(
        number=7, required=False
    ),
    aggregate_value=protox.String(
        number=8, required=False
    ),
)

protox.define_fields(
    SourceCodeInfo.Location,
    path=protox.Int32.as_repeated(
        number=1, packed=True
    ),
    span=protox.Int32.as_repeated(
        number=2, packed=True
    ),
    leading_comments=protox.String(
        number=3, required=False
    ),
    trailing_comments=protox.String(
        number=4, required=False
    ),
    leading_detached_comments=protox.String.as_repeated(
        number=6
    ),
)

protox.define_fields(
    SourceCodeInfo,
    location=SourceCodeInfo.Location.as_repeated(
        number=1
    ),
)

protox.define_fields(
    GeneratedCodeInfo.Annotation,
    path=protox.Int32.as_repeated(
        number=1, packed=True
    ),
    source_file=protox.String(
        number=2, required=False
    ),
    begin=protox.Int32(
        number=3, required=False
    ),
    end=protox.Int32(
        number=4, required=False
    ),
)

protox.define_fields(
    GeneratedCodeInfo,
    annotation=GeneratedCodeInfo.Annotation.as_repeated(
        number=1
    ),
)
