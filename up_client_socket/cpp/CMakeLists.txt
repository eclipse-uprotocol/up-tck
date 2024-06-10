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
project(up_client_socket)

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
    ${CMAKE_SOURCE_DIR}/up-tck/up_client_socket/cpp/src/SocketUTransport.cpp 
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

# Add an library target
add_library(${PROJECT_NAME} ${SOURCE_FILES})
# Comment above line abd uncomment below line to create shared library
#add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

target_include_directories(${PROJECT_NAME}  SYSTEM PUBLIC
						${rapidjson_INCLUDE_DIRS}
						${up-cpp_INCLUDE_DIR}
						${CMAKE_SOURCE_DIR}/up-tck/up_client_socket/cpp/src
						${CMAKE_CURRENT_BINARY_DIR})
						
target_link_libraries(${PROJECT_NAME} PUBLIC
    pthread
    rt
    dl
    ${libs_required}
    libuuid::libuuid
)

INSTALL(TARGETS ${PROJECT_NAME})
INSTALL(DIRECTORY include DESTINATION .)


