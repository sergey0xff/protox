from datetime import datetime

import pytest

from protox.well_known_types import Timestamp
from protox.well_known_types.any import Any


class TestTimestamp:
    def test_valid_datetime(self):
        now = datetime.utcnow()
        message = Timestamp.from_python(now)

        assert isinstance(message.seconds, int)
        assert isinstance(message.nanos, int)

        assert message.to_python() == now

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            Timestamp.from_python(None)


class TestAny:
    def test_valid(self):
        message = Any(
            type_url='https://google.com',
            value=b'12345678'
        )
        assert isinstance(message.type_url, str)
        assert isinstance(message.value, bytes)
