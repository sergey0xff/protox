import protox


class MyMessage(protox.Message):
    empty: protox.Empty


    def __init__(
        self,
        *,
        empty: protox.Empty = None,
    ):
        super().__init__(
            empty=empty,
        )


protox.define_fields(
    MyMessage,
    empty=protox.Empty.as_field(
        number=1, required=True
    ),
)
