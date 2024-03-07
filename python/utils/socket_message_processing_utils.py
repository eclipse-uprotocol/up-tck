# -------------------------------------------------------------------------
#
# Copyright (c) 2024 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import json
import socket
import sys
from typing import Dict

from google.protobuf.any_pb2 import Any
from uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer

sys.path.append("../")

from python.logger.logger import logger
from python.utils.constants import BYTES_MSG_LENGTH


def send_socket_data(s: socket.socket, msg: bytes):
    s.sendall(msg)


def receive_socket_data(s: socket.socket) -> bytes:
    try:
        return s.recv(BYTES_MSG_LENGTH)
    except OSError as oserr:  # in case if socket is closed
        logger.info(oserr)
        return b''


def protobuf_to_base64(obj: Any) -> str:
    serial_proto: bytes = obj.SerializeToString()
    return Base64ProtobufSerializer().deserialize(serial_proto)


def base64_to_protobuf_bytes(base64str: str) -> bytes:
    return Base64ProtobufSerializer().serialize(base64str)


def convert_bytes_to_string(data: bytes) -> str:
    return data.decode()


def convert_jsonstring_to_json(jsonstring: str) -> Dict[str, str]:
    return json.loads(jsonstring)


def convert_json_to_jsonstring(j: Dict[str, str]) -> str:
    return json.dumps(j)


def convert_str_to_bytes(string: str) -> bytes:
    return str.encode(string)
