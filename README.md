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

## Features
* Human-readable python3.6+ generated code with type hinting
* It is easy to use the library without code generation
* Messages implemented in more pythonic way: to_bytes() instead of SerializeToString()
* Enums are just enums python enums
* Useful helper features like to_dict()

## Code generator features
* Root python package with properly resolved imports
* Compile protobuf file with or without dependencies
* [grpclib](https://github.com/vmagamedov/grpclib/) support out of the box

## Difference with google's protobuf implementation
Binary protocol works exactly as google's implementation does.

The difference is in the way messages behave:
* Fields that were not explicitly set are None rather than zero-values
* Methods like SerializeToString() were changed to more pythonic alternatives like to_bytes() / from_bytes()
* Enums are just python int enums

