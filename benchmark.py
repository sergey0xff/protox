import time

import protox


class Point(protox.Message):
    x: int = protox.Int64(number=1, required=True)
    y: int = protox.Int64(number=2, required=True)
    z: int = protox.Int64(number=3, required=True)


p = Point(x=1, y=2, z=3)


# N = 100_000
# before 0.23
# after 0.16
# 0.15
# 0.14
# t = time.monotonic()
# for _ in range(100_000):
#     p.to_bytes()
# print(time.monotonic() - t)

encoded = p.to_bytes()

t = time.monotonic()
for _ in range(100_000):
    Point.from_bytes(encoded)
print(time.monotonic() - t)
