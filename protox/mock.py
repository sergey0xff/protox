from typing import Type, TypeVar, Any

import protox

_field_type_to_value = {
    protox.Int32: 123_456,
    protox.Int64: 123_456,
    protox.SInt32: 123_456,
    protox.SInt64: 123_456,
    protox.UInt32: 123_456,
    protox.UInt64: 123_456,
    protox.Fixed32: 123_456,
    protox.Fixed64: 123_456,
    protox.SFixed32: 123_456,
    protox.SFixed64: 123_456,
    protox.Float: 123.0,
    protox.Double: 123.0,
    protox.Bytes: b'<dummy-bytes>',
    protox.String: '<dummy-string>',
    protox.Bool: True,
}

MessageT = TypeVar('MessageT', bound=protox.Message)


def _mock_field(field: protox.Field) -> Any:
    if isinstance(field, protox.Repeated):
        return [_mock_field(field.field)] * 5
    elif isinstance(field, protox.EnumField):
        return list(field.py_enum)[0]
    elif isinstance(field, protox.MessageField):
        return mock_message(field.of_type)
    elif isinstance(field, protox.MapField):
        key = _mock_field(field.key_field)
        value = _mock_field(field.value_field)
        return {key: value}
    else:
        return _field_type_to_value[type(field)]


def mock_message(
    __message_type__: Type[MessageT],
    **kwargs,
) -> MessageT:
    message: protox.Message = __message_type__()

    for field_name in message.list_fields():
        if field_name in kwargs:
            setattr(
                message,
                field_name,
                kwargs[field_name]
            )
        else:
            field = message._field_by_name[field_name]

            setattr(
                message,
                field_name,
                _mock_field(field)
            )

    return message
