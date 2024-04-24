use std::{io::Write /* , net::TcpStream*/};
use prost_types::field;
use protobuf::reflect::FieldDescriptor;
//use protobuf::reflect::FieldDescriptor;
//use async_std::sync::Mutex;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::runtime::Runtime;
use tokio::sync::mpsc::error;
use tokio::task::spawn_local;
use up_rust::uprotocol::UMessage;
//use up_rust::UAttributes;
//use up_rust::UTransport;
use std::io::Read;
//use std::sync::Arc;
//use std::collections::HashMap;
use protobuf::{Message, MessageDyn, SpecialFields};
use serde::{Deserialize, Serialize};
use up_rust::ulistener::UListener;
use up_rust::{Data, UAttributes, UCode, UMessage, UMessageType, UStatus, UTransport, UUri};
use up_rust::{
    PublishValidator, RequestValidator, ResponseValidator, UAttributesValidator,
    UAttributesValidators, UriValidator,
};
//use up_rust::{
//  rpc::RpcMapper, UTransport, uprotocol::{
//    umessage, UCode, UMessage, UStatus, UUri
//}
//};
use std::{
    collections::HashMap,
    sync::{atomic::AtomicU64, Arc, Mutex},
};


use serde_json::{json, Value};


trait JsonDecoder {
    fn set_value_in_uProtocol(self,  key: &str, value: &[u8]);
    fn field_by_name(self,key:&String)-> Option<FieldDescriptor> ;
    fn mut_field(self, key: &String)-> &mut SpecialFields;
    fn is_some(self,key:&String)-> bool;
   
    fn store(&mut self, item: UMessage) ;
    fn retrieve(&self) -> Option<&UMessage>;
}

struct JsonUMessage{
    uMessage: UMessage,
}


impl JsonDecoder for JsonUMessage{

    fn set_value_in_uProtocol( mut self, key: &str, value: &[u8]) {
        match key {
            "Attributes" => {
                // Set the value in the "Attributes" field

                self.uMessage.attributes.merge_from_bytes(value);
            },
            "Payload" => {
                // Set the value in the "Payload" field
                self.uMessage.payload.merge_from_bytes(value);
            },
            _ => {
                // Handle unknown key or error condition
                println!("Unknown key: {}", key);
            }
        }
    }
    fn field_by_name(self,key:&String)-> Option<FieldDescriptor>{
        self.uMessage.descriptor_dyn().field_by_name(key)

    }
    fn is_some(self,key:&String)-> bool{
        self.uMessage.descriptor_dyn().field_by_name(key).is_some()

    }
    fn mut_field(mut self, key: &String)->&mut SpecialFields
    {
        self.uMessage.mut_special_fields_dyn()
        
      
        //self.uMessage.mut_
    }

    fn store(&mut self, item: UMessage) {
        self.uMessage = item;
    }
    
    fn retrieve(&self) -> Option<&UMessage> {
        Some(&self.uMessage)
    }
    
  
}







pub fn dict_to_proto(mut parent_json_obj: HashMap<String, Value>, parent_proto_obj: &mut dyn JsonDecoder) -> Result<(), Box<dyn std::error::Error>> {
    populate_fields(&mut parent_json_obj, parent_proto_obj)?;
    Ok(())
}

fn populate_fields(json_obj: &mut HashMap<String, Value>, proto_obj: &mut dyn JsonDecoder) -> Result<(), Box<dyn std::error::Error>> {
   // let descriptor = proto_obj.descriptor();
    for (key, value) in json_obj.iter_mut() {
        if let Some(field) = proto_obj.field_by_name(key) {
            if let Some(s) = value.as_str() {
                if s.starts_with("BYTES:") {
                    let byte_string = s.trim_start_matches("BYTES:");
                    let byte_value = base64::decode(byte_string)?;
                    proto_obj.set_value_in_uProtocol(key, &byte_value)
                } else {
                    set_field_value(proto_obj, &field, value)?;
                }
            } else if let Some(sub_message) = proto_obj.store(proto_obj.mut_field(key)) {
            //} else if let Some(sub_message) = proto_obj.field::<dyn Message>(field) {
                if let Some(map) = value.as_object_mut() {
                    populate_fields(map, sub_message)?;
                }
            }
        }
    }
    Ok(())
}

fn set_field_value(proto_obj: &mut dyn JsonDecoder, field: FieldDescriptor, value: &mut Value) -> Result<(), Box<dyn std::error::Error>> {
    match field.runtime_field_type() {
     
       
        prost_types::field::Int32 => {
            let int_value = value.as_i64().ok_or("Invalid value for Int32 field")? as i32;
            proto_obj.set_field(field.number() as usize, int_value);
        }
        prost::encoding::FieldType::Int64 => {
            let int_value = value.as_i64().ok_or("Invalid value for Int64 field")?;
            proto_obj.set_field(field.number() as usize, int_value);
        }
        prost::encoding::FieldType::Float => {
            let float_value = value.as_f64().ok_or("Invalid value for Float field")? as f32;
            proto_obj.set_field(field.number() as usize, float_value);
        }
        prost::encoding::FieldType::Double => {
            let double_value = value.as_f64().ok_or("Invalid value for Double field")?;
            proto_obj.set_field(field.number() as usize, double_value);
        }
        prost::encoding::FieldType::Bool => {
            let bool_value = value.as_bool().ok_or("Invalid value for Bool field")?;
            proto_obj.set_field(field.number() as usize, bool_value);
        }
        prost::encoding::FieldType::String => {
            let string_value = value.as_str().ok_or("Invalid value for String field")?;
            proto_obj.set_field(field.number() as usize, string_value.to_string());
        }
        prost::encoding::FieldType::Message => {
            if let Some(map) = value.as_object_mut() {
                let nested_builder = proto_obj.descriptor().field::<dyn Message>(field).map(|f| f.message_descriptor().new_instance().unwrap());
                if let Some(sub_message) = nested_builder {
                    populate_fields(map, sub_message)?;
                    proto_obj.set_field(field.number() as usize, sub_message);
                }
            }
        }
        _ => {
            // Handle other types as needed
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use prost::Message;
    use serde_json::{json, Value};
    use std::collections::HashMap;

    // Define a simple message struct for testing
    #[derive(Clone, Debug, PartialEq, Message)]
    struct TestMessage {
        #[prost(int32, tag = "1")]
        pub int_field: i32,
        #[prost(string, tag = "2")]
        pub string_field: String,
    }

    #[test]
    fn test_dict_to_proto() {
        // Create a HashMap representing JSON data
        let mut json_obj = HashMap::new();
        json_obj.insert("int_field".to_string(), json!(42));
        json_obj.insert("string_field".to_string(), json!("test_string"));

        // Create a mutable TestMessage instance
        let mut proto_obj = TestMessage {
            int_field: 0,
            string_field: String::new(),
        };

        // Call the dict_to_proto function
        assert!(dict_to_proto(json_obj, &mut proto_obj).is_ok());

        // Check if the TestMessage instance is properly populated
        assert_eq!(proto_obj.int_field, 42);
        assert_eq!(proto_obj.string_field, "test_string");
    }
}