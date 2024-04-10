from typing import Any, Dict, List, Set
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.uri_pb2 import UUri, UResource
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor

def message_to_dict(message: Message) -> Dict[str, Any]:
    """Converts protobuf Message to Dict and keeping respective data types

    Args:
        message (Message): protobuf Message

    Returns:
        Dict[str, Any]: Dict/JSON version of the Message
    """
    result: Dict[str, Any] = {}
    filled_fields: Set[str] = set([field.name for field, _ in message.ListFields()])
    
    all_fields: List[FieldDescriptor] = message.DESCRIPTOR.fields
    for field in all_fields:
        print(field.name, field.label)
        
        value = getattr(message, field.name, field.default_value)
        if isinstance(value, bytes):
            value: str = value.decode()
        
        # if a protobuf Message object
        if hasattr(value, 'DESCRIPTOR'):
            result[field.name] = message_to_dict(value)
        elif field.label == FieldDescriptor.LABEL_REPEATED:
            repeated = []
            for sub_msg in value:
                if hasattr(sub_msg, 'ListFields'):
                    # add Message type protobuf
                    repeated.append(message_to_dict(sub_msg))
                else:
                    # add primitive type (str, bool, bytes, int)
                    repeated.append(value)
            result[field.name] = repeated
        
        # if the field is not a protobuf object (aka, primitive type)
        elif field.label == FieldDescriptor.LABEL_REQUIRED:
            result[field.name] = value
        # if the field is optional and is set
        elif field.label == FieldDescriptor.LABEL_OPTIONAL and field.name in filled_fields:
            result[field.name] = value

    return result

status = UStatus(code=UCode.OK   , message="OK")

print(getattr(UCode, "OK"))
print(message_to_dict(status))

