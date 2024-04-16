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

import logging
import socket
import threading
import time
from collections import defaultdict
from concurrent.futures import Future
from threading import Lock

from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType, CallOptions
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.rpc.rpcclient import RpcClient
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer

logger = logging.getLogger(__name__)
DISPATCHER_ADDR: tuple = ("127.0.0.1", 44444)
BYTES_MSG_LENGTH: int = 32767
RESPONSE_URI = UUri(entity=UEntity(name="test_agent_py", version_major=1), resource=UResourceBuilder.for_rpc_response())


def timeout_counter(response, req_id, timeout):
    time.sleep(timeout / 1000)
    if not response.done():
        response.set_exception(
            TimeoutError('Not received response for request ' + LongUuidSerializer.instance().serialize(
                req_id) + ' within ' + str(timeout / 1000) + ' seconds'))


class SocketUTransport(UTransport, RpcClient):

    def __init__(self):
        """
        Creates a uEntity with Socket Connection, as well as a map of registered topics.
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(DISPATCHER_ADDR)

        self.reqid_to_future = {}
        self.uri_to_listener = defaultdict(list)
        self.lock = Lock()
        thread = threading.Thread(target=self.__listen)
        thread.start()  # with ThreadPoolExecutor(max_workers=5) as executor:  #     executor.submit(self.__listen)

    def __listen(self):
        """
        Listens to UMessages incoming from the Dispatcher.
        Handles incoming data if the Socket_UTransporter is registered to a UUri topic.
        """
        while True:
            try:
                recv_data = self.socket.recv(BYTES_MSG_LENGTH)

                if not recv_data or recv_data == b"":
                    self.socket.close()
                    return
                umsg = UMessage()
                umsg.ParseFromString(recv_data)

                logger.info(f"{self.__class__.__name__} Received uMessage")

                attributes = umsg.attributes
                if attributes.type == UMessageType.UMESSAGE_TYPE_PUBLISH:
                    self._handle_publish_message(umsg)
                elif attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
                    self._handle_request_message(umsg)
                elif attributes.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
                    self._handle_response_message(umsg)

            except socket.error as e:
                logger.error(f"Socket error: {e}")
                self.socket.close()
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    def _handle_publish_message(self, umsg):
        """
        Handles incoming publish messages.
        """
        uri = umsg.attributes.source.SerializeToString()
        self._notify_listeners(uri, umsg)

    def _handle_request_message(self, umsg):
        """
        Handles incoming request messages.
        """

        uri = umsg.attributes.sink.SerializeToString()
        self._notify_listeners(uri, umsg)

    def _notify_listeners(self, uri, umsg):
        """
        Notifies listeners subscribed to the given URI about the incoming message.
        """
        with self.lock:
            listeners = self.uri_to_listener.get(uri, [])
            if listeners:
                logger.info(f"{self.__class__.__name__} Handle Uri")
                for listener in listeners:
                    listener.on_receive(umsg)
            else:
                logger.info(f"{self.__class__.__name__} Uri not found in Listener Map, discarding...")

    def _handle_response_message(self, umsg):
        """
        Handles incoming response messages.
        """
        request_id = umsg.attributes.reqid.SerializeToString()
        with self.lock:
            response_future = self.reqid_to_future.pop(request_id, None)
            if response_future:
                response_future.set_result(umsg)

    def send(self, message: UMessage) -> UStatus:
        """
        Sends the provided UMessage over the socket connection.
        """
        umsg_serialized: bytes = message.SerializeToString()
        try:
            self.socket.sendall(umsg_serialized)
            logger.info(f"uMessage Sent to dispatcher from python socket transport")
        except OSError as e:
            logger.exception(f"INTERNAL ERROR: {e}")
            return UStatus(code=UCode.INTERNAL, message=f"INTERNAL ERROR: {e}")
        return UStatus(code=UCode.OK, message="OK")

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Registers a listener for the specified topic/method URI.
        """

        status = UriValidator.validate(topic)
        if status.is_failure():
            return status.to_status()
        uri: bytes = topic.SerializeToString()
        self.uri_to_listener[uri].append(listener)
        return UStatus(code=UCode.OK, message="OK")

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Unregisters a listener for the specified topic URI.
        """

        status = UriValidator.validate(topic)
        if status.is_failure():
            return status.to_status()
        uri: bytes = topic.SerializeToString()

        listeners = self.uri_to_listener.get(uri, [])

        if listener in listeners:
            listeners.remove(listener)
            if not listeners:
                del self.uri_to_listener[uri]
            return UStatus(code=UCode.OK, message="OK")

        return UStatus(code=UCode.NOT_FOUND, message="Listener not found for the given UUri")

    def invoke_method(self, method_uri: UUri, request_payload: UPayload, options: CallOptions) -> Future:
        """
        Invokes a method with the provided URI, request payload, and options.
        """
        attributes = UAttributesBuilder.request(RESPONSE_URI, method_uri, UPriority.UPRIORITY_CS4,
                                                options.ttl).build()
        # Get uAttributes's request id
        request_id = attributes.id

        response = Future()
        self.reqid_to_future[request_id.SerializeToString()] = response
        # Start a thread to count the timeout
        timeout_thread = threading.Thread(target=timeout_counter, args=(response, request_id, options.ttl))
        timeout_thread.start()

        umsg = UMessage(payload=request_payload, attributes=attributes)
        self.send(umsg)

        return response
