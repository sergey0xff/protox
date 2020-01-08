from datetime import datetime, timezone
from typing import Optional

from protox import Message
from protox import fields

_NANOS_PER_SECOND = 1000000000
_NANOS_PER_MICROSECOND = 1000
_SECONDS_PER_DAY = 24 * 3600


class Timestamp(Message):
    seconds: Optional[int] = fields.Int64(number=1)
    nanos: Optional[int] = fields.Int32(number=2)

    def __init__(
        self,
        seconds: int = None,
        nanos: int = None
    ):
        super().__init__(
            seconds=seconds,
            nanos=nanos
        )

    @classmethod
    def from_python(cls, value) -> 'Timestamp':
        if not isinstance(value, datetime):
            raise ValueError(
                'Expected a datetime value'
            )

        td = value - datetime(
            1970, 1, 1
        )

        return Timestamp(
            seconds=td.seconds + td.days * _SECONDS_PER_DAY,
            nanos=td.microseconds * _NANOS_PER_MICROSECOND
        )

    def to_python(self) -> datetime:
        return datetime.utcfromtimestamp(
            self.seconds + self.nanos / float(_NANOS_PER_SECOND)
        )

    def to_utc(self) -> datetime:
        """
        :returns utc timezone aware datetime object
        """
        return self.to_python().replace(tzinfo=timezone.utc)
