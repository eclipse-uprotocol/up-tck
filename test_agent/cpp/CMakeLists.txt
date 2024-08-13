# SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.10.0)
project(test_agent_cpp VERSION 0.1  LANGUAGES CXX DESCRIPTION "C++ Test Agent")

find_package(protobuf REQUIRED)
find_package(up-core-api REQUIRED)
find_package(up-cpp REQUIRED)
find_package(spdlog REQUIRED)
find_package(fmt REQUIRED CONFIG)
find_package(RapidJSON CONFIG REQUIRED)
find_package(up-transport-socket-cpp REQUIRED)
find_package(OpenSSL REQUIRED)
# TODO: Update when zenoh transport is ready
# find_package(up-client-zenoh-cpp REQUIRED)

# This is the root CMakeLists.txt file; We can set project wide settings here
if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_CURRENT_SOURCE_DIR})
	set(CMAKE_CXX_STANDARD 17)
	# place libraries in a lib directory and executables in a bin directory,
	set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
	set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endif()

file(GLOB_RECURSE SRC_FILES "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")

add_executable(${PROJECT_NAME} ${SRC_FILES})

target_include_directories(${PROJECT_NAME}
	PUBLIC
    ${rapidjson_INCLUDE_DIRS}
	$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
	$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
	$<BUILD_INTERFACE:${CMAKE_BINARY_DIR}>
	${up-transport-socket-cpp_INCLUDE_DIR}
    # ${up-client-zenoh-cpp_INCLUDE_DIR}
	${up-cpp_INCLUDE_DIR}
	${up-core-api_INCLUDE_DIR}
	${protobuf_INCLUDE_DIR}
	${spdlog_INCLUDE_DIR})

set_property(TARGET ${PROJECT_NAME} PROPERTY POSITION_INDEPENDENT_CODE ON)

target_link_libraries(${PROJECT_NAME}
	PRIVATE
    up-transport-socket-cpp::up-transport-socket-cpp
    # up-client-zenoh-cpp::up-client-zenoh-cpp
	up-core-api::up-core-api
	up-cpp::up-cpp
	protobuf::libprotobuf
    pthread
    rt
    dl
    fmt::fmt
    rapidjson
	spdlog::spdlog
    OpenSSL::SSL 
    OpenSSL::Crypto)


INSTALL(TARGETS ${PROJECT_NAME})
INSTALL(DIRECTORY include DESTINATION .)