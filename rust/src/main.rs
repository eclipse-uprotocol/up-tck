/*
 * Copyright (c) 2024 General Motors GTO LLC
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 * SPDX-FileType: SOURCE
 * SPDX-FileCopyrightText: 2023 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

mod constants;
mod uTransportSocket;
mod utils;
/*use std::arch::x86_64::_SIDD_BIT_MASK;
use std::default;
use std::str::FromStr;
use std::u32;*/

//use std::simd::u64x1;

use crate::constants::*;
use crate::uTransportSocket::UtransportExt;
//use crate::utils::convert_str_to_bytes;
use crate::utils::WrapperUMessage;
use log::kv::{value, ToValue};
//use serde::{Deserialize, Deserializer, Serialize};
use testagent::SocketTestAgent;
use uTransportSocket::UtrasnsportSocket;
mod testagent;
use anystruct::{IntoProto, ProtoStruct};
use json2pb::pbgen;
use serde_json::{/*map,*/ Value};
use tokio::net::TcpStream;
use tokio::runtime::Runtime;

// Function to recursively convert log::kv::Value to serde_json::Value
/*fn convert_to_json(value: &log::kv::Value<'_>) -> Value {
    let return_value = match value {


           log::kv::value::Value:: => {Value::String(return_value.to_string())},
            None=>Value::default(),
        }
    //    log::kv::Value::Nil => Value::Null,
   //     log::kv::Value::I64(i) => Value::Number((*i).into()),
     //   log::kv::Value::U64(u) => Value::Number((*u).into()),
      //  log::kv::Value::F64(f) => Value::Number((*f).into()),
       // log::kv::Value::String(s) => Value::String(s.to_string()),
       // log::kv::Value::Map(map) => {
         //   let obj: serde_json::Map<String, Value> = map
           //     .iter()
             //   .map(|(k, v)| (k.to_string(), convert_to_json(v)))
               // .collect();
           // Value::Object(obj)
       // }
        log::kv::Value::Seq(seq) => {
            let vec: Vec<Value> = seq.iter().map(|v| convert_to_json(v)).collect();
            Value::Array(vec)
        }
    }
}*/
/*
fn string_to_json(data: &str) -> Result<Value, serde_json::Error> {
    // Remove leading/trailing whitespaces
    let clean_data = data.trim();

    // Split the data by lines
    let lines = clean_data.split('\n');

    // Collect key-value pairs
    let mut map = serde_json::Map::new();
    for line in lines {
        let mut parts = line.splitn(2, ':');
        let key = parts.next().unwrap().trim();
        let value = parts.next().unwrap_or("").trim();

        // Handle nested structures
        if value.contains('{') {
            let inner_json = string_to_json(value)?;
            map.insert(key.to_string(), inner_json);
        } else {
            // Handle basic types (string, number)
            map.insert(key.to_string(), Value::String(value.to_string()));
        }
    }

    // Convert map to final JSON value
    Ok(Value::Object(map))
}*/

fn string_to_json(string_value: &str) -> Value {
    // Replace spaces with commas to make it valid JSON syntax
    let string_value = string_value.replace(" ", ", ");

    // Add curly braces at the beginning and end to make it a JSON object
    let string_value = format!("{{{}}}", string_value);

    // Parse the modified string into a JSON object
    serde_json::from_str(&string_value).unwrap()
}

fn main() {
    
   
    let transport = UtrasnsportSocket::new();
    let rt = Runtime::new().unwrap();
    rt.block_on(async {
        let test_agent_socket = TcpStream::connect(TEST_MANAGER_ADDR).await.unwrap();

        let mut transport_socket = transport.await;
        transport_socket.socket_init().await;
        let agent = SocketTestAgent::new(test_agent_socket, transport_socket);

        agent.await.receive_from_tm().await;
    });
}
/* 
let json_str2 = r#"
  {
    "attributes": {
      "id": {
        "msb": "111982768538681345",
        "lsb": "9525286032870297316"
      },
      "source": {
        "entity": {
          "name": "body.access:",
          "id": "5"
        },
        "resource": {
          "name": "door",
          "instance": "front_left",
          "message": "Door"
        }
      },
      "type": "UMESSAGE_TYPE_RESPONSE",
      "priority": "UPRIORITY_CS4"
    },
    "payload": {
      "format": "UPAYLOAD_FORMAT_PROTOBUF"
    }
  }"#;

    // Parse JSON to protobuf message
    let json_value: Value = serde_json::from_str(json_str2).unwrap();

    println!("json Message: {:?}", json_value);

    let u_message: WrapperUMessage = serde_json::from_value(json_value).unwrap();

    println!("\n\n Protobuf Message: {:?} \n", u_message);

    let binding = u_message.0.to_string();
    let proto_value = binding.to_value();
    //let proto_string :Value= proto_value.try_into().expect("couldn't conver");
    //let json_data = serde_json::from_value(proto_value);

    println!("\n\n Protobuf Message: {:?} \n", proto_value);

    let json_value = string_to_json(&proto_value.to_string());

    println!("Converted JSON: {}", json_value.to_string());

    // Print JSON object
    println!("{}", serde_json::to_string_pretty(&json_value).unwrap());


*/