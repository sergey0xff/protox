import typing

import protox


class Api(protox.Message):
    name: typing.Optional[str]
    methods: typing.List['Method']
    options: typing.List[protox.Option]
    version: typing.Optional[str]
    source_context: typing.Optional[protox.SourceContext]
    mixins: typing.List['Mixin']
    syntax: typing.Optional[protox.Syntax]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        methods: typing.List['Method'] = None,
        options: typing.List[protox.Option] = None,
        version: typing.Optional[str] = None,
        source_context: typing.Optional[protox.SourceContext] = None,
        mixins: typing.List['Mixin'] = None,
        syntax: typing.Optional[protox.Syntax] = None,
    ):
        super().__init__(
            name=name,
            methods=methods,
            options=options,
            version=version,
            source_context=source_context,
            mixins=mixins,
            syntax=syntax,
        )


class Method(protox.Message):
    name: typing.Optional[str]
    request_type_url: typing.Optional[str]
    request_streaming: typing.Optional[bool]
    response_type_url: typing.Optional[str]
    response_streaming: typing.Optional[bool]
    options: typing.List[protox.Option]
    syntax: typing.Optional[protox.Syntax]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        request_type_url: typing.Optional[str] = None,
        request_streaming: typing.Optional[bool] = None,
        response_type_url: typing.Optional[str] = None,
        response_streaming: typing.Optional[bool] = None,
        options: typing.List[protox.Option] = None,
        syntax: typing.Optional[protox.Syntax] = None,
    ):
        super().__init__(
            name=name,
            request_type_url=request_type_url,
            request_streaming=request_streaming,
            response_type_url=response_type_url,
            response_streaming=response_streaming,
            options=options,
            syntax=syntax,
        )


class Mixin(protox.Message):
    name: typing.Optional[str]
    root: typing.Optional[str]

    def __init__(
        self,
        *,
        name: typing.Optional[str] = None,
        root: typing.Optional[str] = None,
    ):
        super().__init__(
            name=name,
            root=root,
        )


protox.define_fields(
    Api,
    name=protox.String(
        number=1, required=False
    ),
    methods=Method.as_repeated(
        number=2
    ),
    options=protox.Option.as_repeated(
        number=3
    ),
    version=protox.String(
        number=4, required=False
    ),
    source_context=protox.SourceContext.as_field(
        number=5
    ),
    mixins=Mixin.as_repeated(
        number=6
    ),
    syntax=protox.EnumField(
        number=7, py_enum=protox.Syntax, required=False
    ),
)

protox.define_fields(
    Method,
    name=protox.String(
        number=1, required=False
    ),
    request_type_url=protox.String(
        number=2, required=False
    ),
    request_streaming=protox.Bool(
        number=3, required=False
    ),
    response_type_url=protox.String(
        number=4, required=False
    ),
    response_streaming=protox.Bool(
        number=5, required=False
    ),
    options=protox.Option.as_repeated(
        number=6
    ),
    syntax=protox.EnumField(
        number=7, py_enum=protox.Syntax, required=False
    ),
)

protox.define_fields(
    Mixin,
    name=protox.String(
        number=1, required=False
    ),
    root=protox.String(
        number=2, required=False
    ),
)
