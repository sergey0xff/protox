import protox


class MyMessage(protox.Message):
    protox_1: protox.Empty

    def __init__(
        self,
        *,
        protox_1: protox.Empty = None,
    ):
        super().__init__(
            protox_1=protox_1,
        )


protox.define_fields(
    MyMessage,
    protox_1=protox.Empty.as_field(
        number=1, required=True
    ),
)
