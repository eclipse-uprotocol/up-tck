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