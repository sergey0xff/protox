from datetime import datetime

from protox import Message
from protox import fields

_TIMESTAMPFOMAT = '%Y-%m-%dT%H:%M:%S'
_NANOS_PER_SECOND = 1000000000
_NANOS_PER_MILLISECOND = 1000000
_NANOS_PER_MICROSECOND = 1000
_MILLIS_PER_SECOND = 1000
_MICROS_PER_SECOND = 1000000
_SECONDS_PER_DAY = 24 * 3600
_DURATION_SECONDS_MAX = 315576000000


class Timestamp(Message):
    seconds: int = fields.Int64(number=1, required=False)
    nanos: int = fields.Int32(number=2, required=False)

    def __init__(
        self,
        seconds: int = None,
        nanos: int = None
    ):
        super().__init__(
            seconds=seconds,
            nanos=nanos
        )


@Timestamp.set_from_python
def timestamp_from_python(value):
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


@Timestamp.set_to_python
def timestamp_to_python(value: Timestamp):
    return datetime.utcfromtimestamp(
        value.seconds + value.nanos / float(_NANOS_PER_SECOND)
    )
