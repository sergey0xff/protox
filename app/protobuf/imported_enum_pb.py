from enum import IntEnum

import protox


class Hello(protox.Message):
    class Color(IntEnum):
        ONE = 0
