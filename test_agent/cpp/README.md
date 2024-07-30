# Build with Conan package manager

**Note:** The up-tck test agent is only compatible with up-cpp version 1.5.7.

## 1. Setting up docker container (Optional)

To start working in a docker environment, follow these instructions:

- Clone or download the up-conan-recipes repository from [here](https://github.com/gregmedd/up-conan-recipes)
- Navigate to the `tools/ubuntu-24.04-docker` directory
- Run the `launch-shell.sh` script

## 2. Install dependencies to build the CPP test agent

Note: All commands are based on Conan 2. Please adjust the commands accordingly for Conan 1.

Using the recipes found in [up-conan-recipes](https://github.com/eclipse-uprotocol/up-conan-recipes), build these Conan packages:

### up-core-api

```
conan create --version 1.6.0 --build=missing up-core-api/release
```

### up-cpp

```
conan create --version 1.0.1-rc1 --build=missing up-cpp/release/
```

### up_client_socket

```
conan create --version 1.0.0-dev --build=missing up-transport-socket-cpp/developer/
```

## 3. Build the CPP test agent executable

```
cd up-tck/test_agent/cpp/
conan install . --build=missing
cd build
cmake ../ -DCMAKE_TOOLCHAIN_FILE=Release/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build . -- -j
```

## 4. Steps to run with TCK

To run with TCK, follow these steps:

- Navigate to the `up-tck/test_manager` directory
- Run the `testrunner.sh` script
- Provide the feature test name, for example: `register_and_unregister.feature`
- Provide Lauguange1 Under Test `cpp`
- Provide Transport1 Under Test `socket`
- Provide Lauguange2 Under Test `cpp`
- Provide Transport2 Under Test `socket`


