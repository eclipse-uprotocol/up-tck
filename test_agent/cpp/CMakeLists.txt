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

cmake_minimum_required(VERSION 3.20.1)
project(test_agent)
set(APP_NAME test_agent_cpp)

set(CMAKE_CXX_STANDARD 17)

#add_compile_options(-O1 -fPIC -Wall -Wextra -pedantic -Werror -Wcast-qual -Wunused -Wuninitialized -Wmissing-declarations -Wconversion -Wpointer-arith -Wshadow  -Wfloat-equal)

option(DEBUG_BUILD OFF)
if(DEBUG_BUILD)
        message("DEBUG_BUILD Enabled")
        # add_compile_options(-ggdb -fsanitize=address -fno-omit-frame-pointer)
        # add_link_options(-ggdb -fsanitize=address -fno-omit-frame-pointer)
        add_compile_options(-ggdb)
        add_link_options(-ggdb)
endif()

# Specify the source files
set(SOURCE_FILES
    ${CMAKE_SOURCE_DIR}/up-tck/test_agent/cpp/src/TestAgent.cpp
    ${CMAKE_SOURCE_DIR}/up-tck/test_agent/cpp/src/ProtoConverter.cpp   
)

# find and set 
find_package(up-cpp REQUIRED)
find_package(spdlog REQUIRED)
add_definitions(-DSPDLOG_FMT_EXTERNAL)
find_package(fmt REQUIRED CONFIG)
find_package(RapidJSON CONFIG REQUIRED)
find_package(libuuid REQUIRED CONFIG)
find_package(up-client-zenoh-cpp REQUIRED)
find_package(OpenSSL REQUIRED)


set(libs_required
     up-cpp::up-cpp
     spdlog::spdlog
     fmt::fmt
     rapidjson
)

# Add an executable target
add_executable(${APP_NAME} ${SOURCE_FILES})

target_include_directories(${APP_NAME} SYSTEM PUBLIC
						${rapidjson_INCLUDE_DIRS}
						${up-cpp_INCLUDE_DIR}
						${CMAKE_SOURCE_DIR}/up-tck/test_agent/cpp/src
						${CMAKE_SOURCE_DIR}/up-tck/up_client_socket/cpp/src
						${CMAKE_CURRENT_BINARY_DIR})

string(TOLOWER "${CMAKE_BUILD_TYPE}" lowerbuildtype)
						
target_link_directories(${APP_NAME} PUBLIC 
						${CMAKE_SOURCE_DIR}/build-${CMAKE_SYSTEM_PROCESSOR}-${lowerbuildtype}/lib)

target_link_libraries(${APP_NAME} 
    PUBLIC
        up-client-zenoh-cpp::up-client-zenoh-cpp
        ${ZENOH_LIBRARY}
        pthread
        rt
        dl
        ${libs_required}
        libuuid::libuuid
        up_client_socket
        OpenSSL::SSL 
        OpenSSL::Crypto
)

