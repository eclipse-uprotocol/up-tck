"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import logging
import socket
import threading
import time
from collections import defaultdict
from concurrent.futures import Future
from threading import Lock

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.v1.uattributes_pb2 import (
    UMessageType,
)
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus

logger = logging.getLogger(__name__)
DISPATCHER_ADDR: tuple = ("127.0.0.1", 44444)
BYTES_MSG_LENGTH: int = 32767


def timeout_counter(response, req_id, timeout):
    time.sleep(timeout / 1000)
    if not response.done():
        response.set_exception(
            TimeoutError(
                "Not received response for request "
                + UuidSerializer.serialize(req_id)
                + " within "
                + str(timeout / 1000)
                + " seconds"
            )
        )


class SocketUTransport(UTransport, RpcClient):
    def __init__(self, source: UUri):
        """
        Creates a uEntity with Socket Connection, as well as a map of registered topics.
        param source: The URI associated with the UTransport.
        """

        self.source = source
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
            logger.info("uMessage Sent to dispatcher from python socket transport")
        except OSError as e:
            logger.exception(f"INTERNAL ERROR: {e}")
            return UStatus(code=UCode.INTERNAL, message=f"INTERNAL ERROR: {e}")
        return UStatus(code=UCode.OK, message="OK")

    def register_listener(self, source_filter: UUri, listener: UListener, sink_filer: UUri = None) -> UStatus:
        """
        Registers a listener for the specified topic/method URI.
        """

        uri: bytes = source_filter.SerializeToString()
        self.uri_to_listener[uri].append(listener)
        return UStatus(code=UCode.OK, message="OK")

    def unregister_listener(self, source_filter: UUri, listener: UListener, sink_filer: UUri = None) -> UStatus:
        """
        Unregisters a listener for the specified topic URI.
        """

        uri: bytes = source_filter.SerializeToString()

        listeners = self.uri_to_listener.get(uri, [])

        if listener in listeners:
            listeners.remove(listener)
            if not listeners:
                del self.uri_to_listener[uri]
            return UStatus(code=UCode.OK, message="OK")

        return UStatus(
            code=UCode.NOT_FOUND,
            message="Listener not found for the given UUri",
        )

    def invoke_method(self, method_uri: UUri, request_payload: UPayload, options: CallOptions) -> Future:
        """
        Invokes a method with the provided URI, request payload, and options.
        """
        umsg = UMessageBuilder.request(self.source, method_uri, options.timeout).build_from_upayload(request_payload)
        # Get uAttributes's request id
        request_id = umsg.attributes.id

        response = Future()
        self.reqid_to_future[request_id.SerializeToString()] = response
        # Start a thread to count the timeout
        timeout_thread = threading.Thread(target=timeout_counter, args=(response, request_id, options.timeout))
        timeout_thread.start()

        self.send(umsg)

        return response

    def get_source(self) -> UUri:
        """
        Returns the source URI of the UTransport.
        """
        return self.source

    def close(self):
        """
        Closes the socket connection.
        """
        self.socket.close()
        logger.info(f"{self.__class__.__name__} Socket Connection Closed")
