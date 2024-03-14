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


from google.protobuf.any_pb2 import Any
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.umessage_pb2 import UMessage


def set_uuri_fields(proto: UUri, field_name: str, field_value: Any):
    field_name = field_name.lower().strip()
    
    if field_name == "authority":
        proto.authority.CopyFrom(field_value)
    elif field_name == "entity":
        proto.entity.CopyFrom(field_value)
    elif field_name == "resource":
        proto.resource.CopyFrom(field_value)
    else:
        raise ValueError(f"UUri doesn't handle field {field_name}")

def set_umessage_fields(proto: UMessage, field_name: str, field_value: Any):
    field_name = field_name.lower().strip()
    
    if field_name == "attributes":
        proto.attributes.CopyFrom(field_value)
    elif field_name == "payload":
        proto.payload.CopyFrom(field_value)
    else:
        raise ValueError(f"UMessage doesn't handle field {field_name}")