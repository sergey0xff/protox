# Examples
## Encoding / decoding messages
```python
from protox import Message, Int32


class SimpleMessage(Message):
    x: int = Int32(number=1, required=True)


message = SimpleMessage(x=1)
encoded = message.to_bytes()

new_message = SimpleMessage.from_bytes(encoded)
assert new_message == message
```

## Default value
```python
from protox import Message, Int32


class SimpleMessage(Message):
    x: int = Int32(number=1, default=123)


message = SimpleMessage()
assert message.x == 123
```

## Repeated fields
```python
from protox import Message, Int32


class SimpleMessage(Message):
    numbers: int = Int32.as_repeated(number=1)


message = SimpleMessage(numbers=[1, 2, 3])
```

## Message fields
```python
from protox import Message, String


class PhoneNumber(Message):
    number: str = String(number=1, required=True)
    comment: str = String(number=2, required=False)


class User(Message):
    phone_number: PhoneNumber = PhoneNumber.as_field(number=1, required=True)


user = User()
user.phone_number = PhoneNumber(
    number='555 55 55'
)
```

## Repeated message fields
```python
from typing import List

from protox import Message, String


class PhoneNumber(Message):
    number: str = String(number=1, required=True)
    comment: str = String(number=2, required=False)


class User(Message):
    friend_numbers: List[PhoneNumber] = PhoneNumber.as_repeated(number=1)


user = User()
user.friend_numbers.append(
    PhoneNumber(
        number='555 55 55'
    )
)
```

## Enum fields
```python
from enum import IntEnum

from protox import Message, EnumField


class User(Message):
    class Type(IntEnum):
        USER = 1
        ADMIN = 2

    type: Type = EnumField(Type, number=1, required=True)


user = User(type=User.Type.ADMIN)
assert user.type == User.Type.ADMIN
```

## Repeated enum 
```python
from enum import IntEnum
from typing import List

from protox import Message, Repeated


class SimpleMessage(Message):
    class Color(IntEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    colors: List[Color] = Repeated(Color, number=1)


user = SimpleMessage()
user.colors = [
    SimpleMessage.Color.RED,
    SimpleMessage.Color.GREEN
]
```

## Recursive message field
```python
from protox import Message, Int32, define_fields


class Node(Message):
    value: int = Int32(number=1, required=True)
    left: 'Node'
    right: 'Node'

# define fields used for delayed message definition
# to address recursive message definition and circular dependency problems
define_fields(
    Node,
    left=Node.as_field(number=2, required=False),
    right=Node.as_field(number=3, required=False),
)

tree = Node(
    value=10,
    left=Node(
        value=9,
        left=Node(
            value=8
        )
    ),
    right=Node(
        value=11,
        right=Node(
            value=12
        )
    )
)
```

## One of field
```python
from enum import IntEnum

from protox import Message, String, one_of, EnumField


class Response(Message):
    class Error(IntEnum):
        BAD_REQUEST = 0
        INVALID_PARAMS = 1

    class Result(Message):
        message: str = String(number=1, required=True)

    result: Result = Result.as_field(number=1, required=False)
    error: Error = EnumField(Error, number=2, required=False)

    status = one_of(
        'result',
        'error'
    )


response = Response(
    result=Response.Result(
        message='Ok!'
    )
)
assert response.which_one_of('status') == 'result'

error = Response(
    error=Response.Error.BAD_REQUEST
)
assert error.which_one_of('status') == 'error'
```

## Map fields
```python
from typing import Dict

from protox import Message, Int32, MapField, String


class SimpleMessage(Message):
    numbers: Dict[int, str] = MapField(
        key=Int32,
        value=String,
        number=1,
    )


message = SimpleMessage()
message.numbers = {
    1: 'one',
    2: 'two',
    3: 'three',
}
```