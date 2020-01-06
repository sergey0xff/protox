from protox import Message, fields


class Duration(Message):
    seconds: int = fields.Int64(number=1)
    nanos: int = fields.Int32(number=2)

    def __init__(
        self,
        *,
        seconds: int = None,
        nanos: int = None,
    ):
        super().__init__(
            seconds=seconds,
            nanos=nanos,
        )
