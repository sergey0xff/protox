# Protox
Protocol buffers implementation for Python 3 that generates human-readable code with type hinting support

## Quick example
```python
from enum import IntEnum
from protox import Message
from protox import UInt32, String, EnumField


class User(Message):
    class Role(IntEnum):
        USER = 1
        ADMIN = 2

    id: int = UInt32(number=1, required=True)
    email: str = String(number=2, required=True)
    role: Role = EnumField(Role, number=3, required=True, default=Role.USER)


user = User(id=1, email="john@doe.com", role=User.Role.USER)
user_data = user.to_bytes()

print(User.from_bytes(user_data))
# Outputs:
# message User
#     id = 1
#     email = 'john@doe.com'
#     role = Role.USER
```

## More examples 
* [EXAMPLES.md](EXAMPLES.md)
* [Grpclib example](grpclib_example)

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

#### Generate grpclib service with all required dependencies 
The following code generates service `ping_pong.proto` from the `protobuf_src` directory into `{$PROJECT_ROOT}/app/protobuf`.

The protox plugin supports 3 options:
* --base-package=path/to/protobuf/out 
* --grpclib  # generates grpclib services 
* --with-dependencies  # generates dependencies for the given protobuf file

The options to the plugin are passed using the `--protox_opt="{plugin options here}"` command 
```bash
protoc \
    --proto_path=protobuf_src \
    --protox_out=. \
    --protox_opt="--base-package=app/protobuf --grpclib --with-dependencies" \
    ./protobuf_src/ping_pong.proto
```


## Core concepts 
* Human-readable python3.6+ generated code with type hinting
* Support protobuf 2 and 3 at the same time
* `None` values instead of zero values in fields for both proto2 and proto3
* `Message.has_field()` in both proto2 and proto3
* Protocols are easy to describe without code generation 
* Messages implemented in more pythonic way: to_bytes() instead of SerializeToString()
* Enums are just enums python int enums

## Features
- [x] Messages
- [x] Enums
- [x] Nested messages
- [x] Maps
- [x] Well-known types
- [x] Repeated fields
- [x] Repeated messages
- [x] Repeated enums
- [x] Custom Message.to_python() / from_python() functions
- [ ] Group fields (Deprecated by protobuf)


## Code generator features
- [x] Protobuf
- [x] [Grpclib](https://github.com/vmagamedov/grpclib/)
- [ ] [Grpc.io](https://github.com/grpc/grpc/tree/master/src/python/grpcio)
- [x] Custom python package for protobuf out messages
- [x] Compile protobuf file with dependencies
- [x] Names mangling to avoid reserved names collisions
- [x] Recursive messages/enums support
- [x] Field names to_snake_case support

## Difference with google's protobuf implementation
Binary protocol works exactly as google's implementation does.

The difference is in the way messages behave:
* Fields that were not explicitly set are None rather than zero-values
* Methods like SerializeToString() were changed to more pythonic alternatives like to_bytes() / from_bytes()
* Enums are just python int enums

## Generated code example
[Grpclib service example](grpclib_example/app/protobuf/service_grpclib.py)

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
