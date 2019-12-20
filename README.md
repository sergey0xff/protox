# Protobuf for humans
protox is a protobuf implementation for Python 3 that generates human-readable python code 

## Disclaimer
It is alpha version yet fully working binary protocol

## Features
* Human-readable python3.6+ generated code with type hinting
* It is easy to use the library without code generation
* Messages implemented in more pythonic way: to_bytes() instead of SerializeToString()
* Enums are just enums python enums
* Useful helper features like to_dict()
* You can choose the python module to put generated protobufs to

## Coming soon features
* Compiler

## Difference with google's protobuf implementation
Fields encoded/decoded exactly as google's implementation does
Difference is only in how messages behave
* Not set fields are None, not zero-values.
Makes no sense in setting zero-values for fields in Python
* Some of the google's methods like SerializeToString() were changed to more pythonic alternatives like dump(s)/load(s)
* Enums are just python int enums. 
Google's implementation stores enum values as constants of parent objects which is also makes no sense in python.

## Describe a simple message by hand and send it another python process
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

Or generate it from a .proto file

```bash
python3.7 -m protox --src=protobuf_src --python-out=protobuf
```
