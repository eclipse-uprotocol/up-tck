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

from uprotocol.proto.upayload_pb2 import UPayloadFormat 

def type_converter(type: str, data: str):
    type = type.lower().strip()
    
    if type in ["int", "integer"]:
        return int(data)
    elif type in ["bytes"]:
        return data.encode()
    elif type in ["str", "string"]:
        return data
    elif type in ["upayload_format"]:
        return UPayloadFormat.Value(data)
    else:
        raise ValueError(f"type_converter() doesn't handle type {type}")
    