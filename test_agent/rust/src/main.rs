/*
 * SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * SPDX-FileType: SOURCE
 * SPDX-License-Identifier: Apache-2.0
 */

mod constants;

mod utils;

use std::{sync::Arc, thread};

use crate::constants::{TEST_MANAGER_ADDR, ZENOH_TRANSPORT};
use testagent::{ListenerHandlers, SocketTestAgent};
use up_rust::{Number, UAuthority, UEntity, UTransport};
use utransport_socket::UTransportSocket;
mod testagent;
use clap::Parser;
use log::{debug, error};
use std::net::TcpStream;
use tokio::runtime::Runtime;
use up_client_zenoh::UPClientZenoh;
use zenoh::config::Config;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Transport with which to run rust TA
    #[arg(short, long)]
    transport: String,
}

fn connect_to_socket(addr: &str, port: u16) -> Result<TcpStream, Box<dyn std::error::Error>> {
    let socket_addr = format!("{addr}:{port}");
    match TcpStream::connect(socket_addr) {
        Ok(socket) => Ok(socket),
        Err(err) => {
            error!("Error connecting socket: {}", err);
            Err(Box::new(err))
        }
    }
}

async fn create_zenoh_u_transport() -> Box<dyn UTransport> {
    let uauthority = UAuthority {
        name: Some("MyAuthName".to_string()),
        number: Some(Number::Id(vec![1, 2, 3, 4])),
        ..Default::default()
    };
    let uentity = UEntity {
        name: "default.entity".to_string(),
        id: Some(u32::from(rand::random::<u16>())),
        version_major: Some(1),
        version_minor: None,
        ..Default::default()
    };
    dbg!("zenoh transport created successfully");

    Box::new(
        UPClientZenoh::new(Config::default(), uauthority, uentity)
            .await
            .unwrap(),
    )
}

async fn connect_and_receive(transport_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let test_agent = connect_to_socket(TEST_MANAGER_ADDR.0, TEST_MANAGER_ADDR.1)?;
    let ta_to_tm_socket = connect_to_socket(TEST_MANAGER_ADDR.0, TEST_MANAGER_ADDR.1)?;
    let foo_listener_socket_to_tm = connect_to_socket(TEST_MANAGER_ADDR.0, TEST_MANAGER_ADDR.1)?;

    #[allow(clippy::single_match_else)]
    // We allow this because we'll have further transports we want to support and match works well
    // for that
    let u_transport: Box<dyn UTransport> = match transport_name {
        ZENOH_TRANSPORT => create_zenoh_u_transport().await,
        _ => {
            debug!("Socket transport created successfully");
            Box::new(UTransportSocket::new()?)
        }
    };

    let foo_listener = Arc::new(ListenerHandlers::new(foo_listener_socket_to_tm));
    let agent = SocketTestAgent::new(test_agent, foo_listener);
    agent
        .clone()
        .receive_from_tm(u_transport, ta_to_tm_socket)
        .await;

    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let handle = thread::spawn(|| {
        let args = Args::parse();
        let transport_name = args.transport;

        println!("Transport Name: {transport_name}");

        let rt = Runtime::new().expect("error creating run time");

        match rt.block_on(connect_and_receive(&transport_name)) {
            Ok(()) => (),
            Err(err) => eprintln!("Error occurred: {err}"),
        };
    });

    if let Err(err) = handle.join() {
        eprintln!("Error joining thread: {err:?}");
        std::process::exit(1);
    } else {
        debug!("Successfully joined thread");
    }
    Ok(())
}
