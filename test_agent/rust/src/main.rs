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
use up_rust::UTransport;
mod testagent;
use clap::Parser;
use log::{debug, error};
use std::net::TcpStream;
use std::str::FromStr;
use tokio::runtime::Runtime;
use up_transport_zenoh::UPClientZenoh;
use zenoh::config::{Config, EndPoint};

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
    dbg!("zenoh transport created successfully");

    let mut zenoh_config = Config::default();

    // Specify the address to listen on using IPv4
    let ipv4_endpoint = EndPoint::from_str("tcp/0.0.0.0:7445");

    // Add the IPv4 endpoint to the Zenoh configuration
    zenoh_config
        .listen
        .endpoints
        .push(ipv4_endpoint.expect("FAIL"));
    // TODO: Add error handling if we fail to create a UPClientZenoh
    Box::new(
        UPClientZenoh::new(zenoh_config, "windows".to_string())
            .await
            .unwrap(),
    )
}

async fn connect_and_receive(transport_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let test_agent = connect_to_socket(TEST_MANAGER_ADDR.0, TEST_MANAGER_ADDR.1)?;
    let ta_to_tm_socket = connect_to_socket(TEST_MANAGER_ADDR.0, TEST_MANAGER_ADDR.1)?;
    let foo_listener_socket_to_tm = connect_to_socket(TEST_MANAGER_ADDR.0, TEST_MANAGER_ADDR.1)?;

    #[allow(clippy::match_same_arms)]
    // We allow this because we'll have further transports we want to support and match works well
    // for that
    let u_transport: Box<dyn UTransport> = match transport_name {
        ZENOH_TRANSPORT => create_zenoh_u_transport().await,
        _ => create_zenoh_u_transport().await,
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
