from typing import Optional

from protox import Message, fields


class SourceContext(Message):
    file_name: Optional[str] = fields.String(number=1)

    def __init__(
        self,
        *,
        file_name: str = None,
    ):
        super().__init__(
            file_name=file_name
        )
