from datetime import datetime, timezone, timedelta
from typing import Optional

from protox import Message
from protox import fields

_nanos_per_second = 1000000000
_nanos_per_millisecond = 1000000
_nanos_per_microsecond = 1000
_millis_per_second = 1000
_micros_per_second = 1000000

_timestamp_format = '%Y-%m-%dT%H:%M:%S'
_seconds_per_day = 24 * 3600


class TimestampParseError(Exception):
    pass


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
    def from_json_string(cls, json_string: str) -> 'Timestamp':
        timezone_offset = json_string.find('Z')

        if timezone_offset == -1:
            timezone_offset = json_string.find('+')

        if timezone_offset == -1:
            timezone_offset = json_string.rfind('-')

        if timezone_offset == -1:
            raise TimestampParseError(
                'Failed to parse timestamp: missing valid timezone offset.'
            )

        time_value = json_string[0:timezone_offset]

        point_position = time_value.find('.')

        if point_position == -1:
            second_value = time_value
            nano_value = ''
        else:
            second_value = time_value[:point_position]
            nano_value = time_value[point_position + 1:]

        date_object = datetime.strptime(second_value, _timestamp_format)
        td = date_object - datetime(1970, 1, 1)
        seconds = td.seconds + td.days * _seconds_per_day

        if len(nano_value) > 9:
            raise TimestampParseError(
                'Failed to parse Timestamp: nanos {0} more than '
                '9 fractional digits.'.format(nano_value)
            )

        if nano_value:
            nanos = round(float('0.' + nano_value) * 1e9)
        else:
            nanos = 0

        # Parse timezone offsets.
        if json_string[timezone_offset] == 'Z':
            if len(json_string) != timezone_offset + 1:
                raise TimestampParseError(
                    'Failed to parse timestamp: invalid trailing'
                    ' data {0}.'.format(json_string)
                )
        else:
            tz = json_string[timezone_offset:]
            pos = tz.find(':')

            if pos == -1:
                raise TimestampParseError(
                    'Invalid tz offset value: {0}.'.format(tz)
                )

            if tz[0] == '+':
                seconds -= (int(tz[1:pos]) * 60 + int(tz[pos + 1:])) * 60
            else:
                seconds += (int(tz[1:pos]) * 60 + int(tz[pos + 1:])) * 60

        return cls(
            seconds=int(seconds),
            nanos=int(nanos)
        )

    @classmethod
    def from_nanoseconds(cls, nanos: int) -> 'Timestamp':
        return Timestamp(
            seconds=nanos // _nanos_per_second,
            nanos=nanos % _nanos_per_second,
        )

    @classmethod
    def from_microseconds(cls, micros: int) -> 'Timestamp':
        return Timestamp(
            seconds=micros // _micros_per_second,
            nanos=(micros % _micros_per_second) * _nanos_per_microsecond,
        )

    @classmethod
    def from_milliseconds(cls, millis: int) -> 'Timestamp':
        return Timestamp(
            seconds=millis // _millis_per_second,
            nanos=(millis % _millis_per_second) * _nanos_per_millisecond,
        )

    @classmethod
    def from_seconds(cls, seconds: int) -> 'Timestamp':
        return Timestamp(
            seconds=seconds,
            nanos=0,
        )

    @classmethod
    def from_datetime(cls, dt: datetime) -> 'Timestamp':
        td = dt - datetime(
            1970, 1, 1
        )

        return Timestamp(
            seconds=td.seconds + td.days * _seconds_per_day,
            nanos=td.microseconds * _nanos_per_microsecond
        )

    @classmethod
    def from_utc(cls, value: datetime) -> 'Timestamp':
        return cls.from_datetime(
            value.replace(tzinfo=None)
        )

    @classmethod
    def now(cls) -> 'Timestamp':
        return cls.from_datetime(
            datetime.now()
        )

    @classmethod
    def utcnow(cls) -> 'Timestamp':
        return cls.from_datetime(
            datetime.utcnow()
        )

    def to_json_string(self) -> str:
        nanos = self.nanos % _nanos_per_second
        total_sec = self.seconds + (self.nanos - nanos) // _nanos_per_second
        seconds = total_sec % _seconds_per_day
        days = (total_sec - seconds) // _seconds_per_day
        dt = datetime(1970, 1, 1) + timedelta(days, seconds)

        result = dt.isoformat()

        if nanos % 1e9 == 0:
            return result + 'Z'

        if nanos % 1e6 == 0:
            return result + '.%03dZ' % (nanos / 1e6)

        if nanos % 1e3 == 0:
            return result + '.%06dZ' % (nanos / 1e3)

        return result + '.%09dZ' % nanos

    def to_nanoseconds(self) -> int:
        return self.seconds * _nanos_per_second + self.nanos

    def to_microseconds(self) -> int:
        return (
            self.seconds * _micros_per_second +
            self.nanos // _nanos_per_microsecond
        )

    def to_milliseconds(self) -> int:
        return (
            self.seconds * _millis_per_second +
            self.nanos // _nanos_per_millisecond
        )

    def to_seconds(self) -> int:
        return self.seconds

    def to_datetime(self, tzinfo: timezone = None) -> datetime:
        return datetime.utcfromtimestamp(
            self.seconds + self.nanos / float(_nanos_per_second)
        ).replace(tzinfo=tzinfo)

    def to_utc(self) -> datetime:
        return self.to_datetime(timezone.utc)
