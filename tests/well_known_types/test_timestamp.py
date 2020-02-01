from datetime import datetime, timedelta

from protox.well_known_types import Timestamp


def test_now():
    ts_now = Timestamp.now().to_datetime()

    assert datetime.now() - ts_now < timedelta(seconds=1)


def test_utcnow():
    ts_utcnow = Timestamp.utcnow().to_datetime()

    assert datetime.utcnow() - ts_utcnow < timedelta(seconds=1)


def test_datetime():
    now = datetime.utcnow()
    ts = Timestamp.from_datetime(now)

    assert isinstance(ts.seconds, int)
    assert isinstance(ts.nanos, int)
    assert ts.to_datetime() == now


def test_from_json_string():
    original_ts = Timestamp.now()
    ts_from_json_string = Timestamp.from_json_string(
        original_ts.to_json_string()
    )

    assert ts_from_json_string == original_ts


def test_from_nanoseconds():
    original_ts = Timestamp.now()
    ts_from_nanoseconds = Timestamp.from_nanoseconds(
        original_ts.to_nanoseconds()
    )

    assert ts_from_nanoseconds == original_ts


def test_from_microseconds():
    original_ts = Timestamp.now()
    ts_from_microseconds = Timestamp.from_microseconds(
        original_ts.to_microseconds()
    )

    assert ts_from_microseconds == original_ts


def test_from_milliseconds():
    original_ts = Timestamp.now()
    ts_from_milliseconds = Timestamp.from_milliseconds(
        original_ts.to_milliseconds()
    )

    assert ts_from_milliseconds.seconds == original_ts.seconds
    assert ts_from_milliseconds.nanos == int(original_ts.nanos / 10 ** 6) * 10 ** 6


def test_from_seconds():
    original_ts = Timestamp.now()
    ts_from_seconds = Timestamp.from_seconds(
        original_ts.to_seconds()
    )

    assert ts_from_seconds.seconds == original_ts.seconds
