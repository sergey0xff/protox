import typing

import protox


class FieldMask(protox.Message):
    paths: typing.List[str]

    def __init__(
        self,
        *,
        paths: typing.List[str] = None,
    ):
        super().__init__(
            paths=paths,
        )


protox.define_fields(
    FieldMask,
    paths=protox.String.as_repeated(
        number=1
    ),
)
