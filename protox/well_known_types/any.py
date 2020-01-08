from typing import Optional

from protox import Message, fields


class Any(Message):
    type_url: Optional[str] = fields.String(number=1)
    value: Optional[bytes] = fields.Bytes(number=2)

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
