# Build with Conan package manager

**Note:** The up-tck test agent is only compatible with up-cpp version 1.5.7.

## 1. Setting up docker container (Optional)

To start working in a docker environment, follow these instructions:

- Clone or download the up-conan-recipes repository from [here](https://github.com/gregmedd/up-conan-recipes)
- Navigate to the `tools/ubuntu-24.04-docker` directory
- Run the `launch-shell.sh` script

## 2. Install dependencies to build the CPP test agent

Note: All commands are based on Conan 2. Please adjust the commands accordingly for Conan 1.

### up-cpp

```
git clone https://github.com/eclipse-uprotocol/up-cpp.git
cd up-cpp
git checkout up-v1.5.7
git submodule update --init --recursive
conan create . --build=missing
```

### zenohc

```
git clone https://github.com/eclipse-zenoh/zenoh-c.git
cd zenoh-c
git checkout release/0.11.0.3
mkdir -p ../build && cd ../build 
cmake ../zenoh-c
cmake --build . --config Release
cmake --build . --target install
```

### up-transport-zenoh-cpp

```
git clone https://github.com/eclipse-uprotocol/up-transport-zenoh-cpp.git
cd up-cpp-client-zenoh
git checkout v0.1.3-dev
conan create . --build=missing
```

### up_client_socket

```
git clone https://github.com/eclipse-uprotocol/up-tck.git
cd up-tck/up_client_socket/cpp
conan create --version=up_client_socket/0.1.0 --build=missing .
```

## 3. Build the CPP test agent executable

```
cd up-tck/test_agent/cpp/
conan install .
cd build
cmake ../ -DCMAKE_TOOLCHAIN_FILE=Release/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build . -- -j
```

## 4. Steps for execution

To run the CPP test agent standalone, execute the following command:

```
./test_agent_cpp --transport {zenoh/socket}
```

## 5. Steps to run with TCK

To run with TCK, follow these steps:

- Create a target folder and copy the contents of `build-x86_64-release` to `up-tck/test_agent/cpp/target` folder
- Navigate to the `up-tck/test_manager` directory
- Run the `testrunner.sh` script
- Provide the feature test name, for example: `register_and_unregister`

