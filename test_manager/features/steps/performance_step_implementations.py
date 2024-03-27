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
import base64
import codecs
import time

from behave import step
from behave.runner import Context
from hamcrest import assert_that, equal_to, less_than, is_

@step(u'"{publisher}" sets up publisher and "{subscriber}" sets up subscriber')
def set_publisher_subscriber(context, publisher: str, subscriber: str):
    context.pub_timeout = False
    context.pub_msgs = []
    context.sub_msgs = []
    context.logger.info(f"Publisher: {publisher}, Subscriber: {subscriber}")

@step(u'user waits for publisher timeout')
def wait_for_timeout(context):
    while not context.pub_timeout:
        time.sleep(1)

@step(u'average latency is less than "{average_latency}" in milliseconds')
def get_average_latency(context, average_latency: str):
    pub_msgs = context.pub_msgs
    sub_msgs = context.sub_msgs
    result, average_lat = join_lists_by_common_id(pub_msgs, sub_msgs)
    assert_that(average_lat, is_(less_than(float(average_latency))))


def join_lists_by_common_id(list1, list2):
    # Step 1: Create dictionaries to map common IDs to dictionaries
    dict1 = {item["id"]: item for item in list1}
    dict2 = {item["id"]: item for item in list2}

    # Step 2: Merge dictionaries with the same common ID
    result = []
    latencies = {}
    common_ids = set(dict1.keys()).intersection(dict2.keys())
    for common_id in common_ids:
        merged_dict = dict1[common_id].copy()
        merged_dict.update(dict2[common_id])

        # Calculate latency and store it
        published_time = dict1[common_id]["published_timestamp"]
        received_time = dict2[common_id]["received_timestamp"]
        latency = int(received_time) - int(published_time)
        latencies[common_id] = latency

        result.append(merged_dict)

    # Step 3: Handle unmatched common IDs
    for common_id in set(dict1.keys()).difference(dict2.keys()):
        result.append(dict1[common_id])
    for common_id in set(dict2.keys()).difference(dict1.keys()):
        result.append(dict2[common_id])

    # Calculate average latency
    average_latency = sum(latencies.values()) / len(latencies.values()) if len(latencies) > 0 else 0

    return result, average_latency