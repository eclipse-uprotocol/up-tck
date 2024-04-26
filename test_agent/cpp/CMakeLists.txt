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

cmake_minimum_required(VERSION 3.20.1)
project(testagent)
set(APP_NAME testagent-app)

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
    ${CMAKE_SOURCE_DIR}/testagent/src/SocketUTransport.cpp
    ${CMAKE_SOURCE_DIR}/testagent/src/TestAgent.cpp
    ${CMAKE_SOURCE_DIR}/testagent/src/ProtoConverter.cpp   
)

# find and set 
find_package(up-cpp REQUIRED)
find_package(spdlog REQUIRED)
add_definitions(-DSPDLOG_FMT_EXTERNAL)
find_package(fmt REQUIRED CONFIG)
find_package(RapidJSON CONFIG REQUIRED)
find_package(libuuid REQUIRED CONFIG)

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
						${CMAKE_SOURCE_DIR}/testagent/src
						${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(${APP_NAME} PUBLIC
    pthread
    rt
    dl
    ${libs_required}
    libuuid::libuuid
)

