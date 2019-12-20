from typing import Dict

from protox import fields, Message
from protox.fields import MapField


class DictMessage(Message):
    dictionary: Dict[str, int] = MapField(
        key=fields.String,
        value=fields.Int32,
        number=1
    )
