# Build with conan package manager:
-----------------------------------
# 1. Setting up docker container 
#### instructions for **** Start working in uDev environment ****
https://confluence.ultracruise.gm.com/display/UL/GitHub+-+uSpace+%28Ultifi%29+-+Quick+start

#### Create projects directory
cd ~; mkdir ~/projects; cd ~/projects
#### Create ufw_workspace
git clone https://github.com/GM-SDV-UP/gmultifi_ufw_workspace.git uspace_deploy; cd uspace_deploy
#### execute init repo script
./init_ultifi_repo.sh
#### Login to docker artifactory (use your gm credentials):
docker login artifactory.ultracruise.gm.com
#### Run uDev container;
./ubox.sh

# 2. preparing the build environment
#### from the uDev container
cd ~/projects/uspace_deploy/ultifi
#### clone cpp testagent
mkdir testagent 
cd testagent
##### Download and test agent code from https://github.com/eclipse-uprotocol/up-tck/test_agent/cpp to testagent folder

#### create the main CMAKE file
cat << EOF > CMakeLists.txt
cmake_minimum_required(VERSION 3.20.0)
project(ultifi)
 
set(CONANFILES_ROOT \${CMAKE_CURRENT_SOURCE_DIR})
include(cmake/CmakeCommonInit.cmake)
add_repo(testagent)
EOF
 
#### Set the path of the 'conanfile.py'. Will be used by the UFW-Build-System.
rm conanfile.py

ln -sf testagent/conanfile.py conanfile.py

# 3. compiling 
#### from the uDev container
cd ~/projects/uspace_deploy/ultifi
#### To build for uDev docker
#### To build release 
source build.sh -r 
#### To build debug 
source build.sh -d
#### Note: if you got compilation error regarding UPayload and UAttributes ambiguous, 
####       go to your conan folder path and modify RPC client with full path for UPayload and UAttributes as shown below.
vim ~/.conan/data/up-cpp/0.1.5.0-dev/_/_/package/89f3c5e59c749f26b20b069c0b4afb8e0cc77bac/include/up-cpp/rpc/RpcClient.h
virtual std::future<uprotocol::utransport::UPayload> invokeMethod(const UUri &topic,
                                                   const uprotocol::utransport::UPayload &payload,
                                                   const uprotocol::utransport::UAttributes &attributes) = 0;
# 4. Step for execution 
#### if you built build-x86_64-release
cd build-x86_64-release/bin

#### run the below executable for standalone launch of cpp testagent
./testagent-app

# 5. Steps to run with TCK
#### copy the contents of build-x86_64-release to up-tck/test_agent/cpp/target folder
cp -rf build-x86_64-release/bin up-tck/test_agent/cpp/target/
cd up-tck/test_manager
sh testrunner.sh
####  provide feature test name say register_and_unregister
register_and_unregister

