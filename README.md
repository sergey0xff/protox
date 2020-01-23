# Protox
Protobuf implementation for Python 3 that generates human-readable code with type hinting support

## Quick example
```python
from enum import IntEnum
from protox import Message
from protox import UInt32, String, EnumField

class User(Message):
    class Status(IntEnum):
        USER = 1
        ADMIN = 2       
        
    id: int = UInt32(number=1, required=True)
    email: str = String(number=2, required=True)
    status: Status = EnumField(Status, number=3, required=True, default=Status.USER)
```

## Code generation
Code generator implemented as a protoc plugin so you have to install it first:

#### Install protoc (Ubuntu)
```bash
sudo apt install protobuf-compiler
```

#### Install protoc (Mac OS)
```bash
brew install protobuf
```

#### Install protox
```bash
python3 -m pip install protox
````

#### Generate messages
```bash
protoc \
    --proto_path=protobuf_src \
    --protox_out=. \
    ./protobuf_src/user.proto
```

## Core concepts 
* Human-readable python3.6+ generated code with type hinting
* Protocols are easy to describe without code generation 
* Messages implemented in more pythonic way: to_bytes() instead of SerializeToString()
* Enums are just enums python enums
* Useful helper features like to_dict()

## Features
*[x] Messages
*[x] Enums
*[x] Nested messages
*[x] Maps
*[x] Well-known types
*[x] Repeated fields
*[x] Repeated messages
*[x] Repeated enums
*[x] Custom Message.to_python() / from_python() functions
*[x] Code generator
    *[x] Protobuf
    *[x] Grpclib
    *[ ] Grpc

## Code generator features
* Root python package with properly resolved imports
* Compile protobuf file with or without dependencies
* Names mangling to avoid reserved name collisions 
* Recursive messages/enums support using deferred field declaration
* Field names to_snake_case support
* [grpclib](https://github.com/vmagamedov/grpclib/) support out of the box

## Difference with google's protobuf implementation
Binary protocol works exactly as google's implementation does.

The difference is in the way messages behave:
* Fields that were not explicitly set are None rather than zero-values
* Methods like SerializeToString() were changed to more pythonic alternatives like to_bytes() / from_bytes()
* Enums are just python int enums

## Generated code example
```python
from enum import IntEnum

import protox


class User(protox.Message):
    class Status(IntEnum):
        USER = 1
        ADMIN = 2

    id: int
    email: str
    status: 'User.Status'

    def __init__(
        self,
        *,
        id: int = None,
        email: str = None,
        status: 'User.Status' = None,
    ):
        super().__init__(
            id=id,
            email=email,
            status=status,
        )


protox.define_fields(
    User,
    id=protox.Int32(
        number=1, required=True
    ),
    email=protox.String(
        number=2, required=True
    ),
    status=protox.EnumField(
        number=3, py_enum=User.Status, default=User.Status.USER, required=True
    ),
)
```