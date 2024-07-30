# Local build steps for SocketUTransport
*From the up_client_socket/cpp directory, run the following commands*
1. conan install --build=missing .
2. cmake --preset conan-release
3. (cd build/Release; cmake --build . -- -j)
