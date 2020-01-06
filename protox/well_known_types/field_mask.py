from typing import List

from protox import Message, fields


class FieldMask(Message):
    paths: List[str] = fields.String.as_repeated(number=1)
