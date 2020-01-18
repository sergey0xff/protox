import typing

import protox


class SourceContext(protox.Message):
    file_name: typing.Optional[str]

    def __init__(
        self,
        *,
        file_name: typing.Optional[str] = None,
    ):
        super().__init__(
            file_name=file_name,
        )


protox.define_fields(
    SourceContext,
    file_name=protox.String(
        number=1, required=False
    ),
)
