from protox import Message, fields


class Any(Message):
    type_url: str = fields.String(number=1, required=False)
    value: bytes = fields.Bytes(number=2, required=False)

    def __init__(
        self,
        *,
        type_url: str = None,
        value: bytes = None
    ):
        super().__init__(
            type_url=type_url,
            value=value,
        )
