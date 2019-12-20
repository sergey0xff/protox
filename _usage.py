from app.protobuf.hello_protox_pb import User

User(
    id=1,
    name='hello',
    type=User.Type.ADMIN,
)
