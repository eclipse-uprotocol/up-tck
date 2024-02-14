from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType


def get_priority(priority: str) -> UPriority :
        priority = priority.strip()
        
        if priority == "UPRIORITY_UNSPECIFIED":
            return UPriority.UPRIORITY_UNSPECIFIED 
        
        elif priority == "UPRIORITY_CS0":
            return UPriority.UPRIORITY_CS0 
        
        elif priority == "UPRIORITY_CS1":
            return UPriority.UPRIORITY_CS1 
        
        elif priority == "UPRIORITY_CS2":
            return UPriority.UPRIORITY_CS2 
        
        elif priority == "UPRIORITY_CS3":
            return UPriority.UPRIORITY_CS3 
        
        elif priority == "UPRIORITY_CS4":
            return UPriority.UPRIORITY_CS4 
        
        elif priority == "UPRIORITY_CS5":
            return UPriority.UPRIORITY_CS5 
        
        elif priority == "UPRIORITY_CS6":
            return UPriority.UPRIORITY_CS6 
        else:
            raise Exception("UPriority value not handled")
    
def get_umessage_type(umessage_type: str) -> UMessageType :
    umessage_type = umessage_type.strip()
    
    if umessage_type == "UMESSAGE_TYPE_UNSPECIFIED":
        return UMessageType.UMESSAGE_TYPE_UNSPECIFIED 
    
    elif umessage_type == "UMESSAGE_TYPE_PUBLISH":
        return UMessageType.UMESSAGE_TYPE_PUBLISH 
    
    elif umessage_type == "UMESSAGE_TYPE_REQUEST":
        return UMessageType.UMESSAGE_TYPE_REQUEST 
    
    elif umessage_type == "UMESSAGE_TYPE_RESPONSE":
        return UMessageType.UMESSAGE_TYPE_RESPONSE 
    else:
        raise Exception("UMessageType value not handled!")