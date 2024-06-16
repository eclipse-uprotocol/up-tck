import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Git


class UpClientSocket(ConanFile):
    name = "up_client_socket"

    # Optional metadata
    license = "Apache-2.0 license"
    author = "<Put your name here> <And your email here>"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ up client socket library for testagent"
    topics = ("ulink client", "transport")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "fork": ["ANY"], "commitish": ["ANY"]}

    default_options = {"shared": False, "fPIC": True, "fork": "agosh01/up-tck", "commitish": "add_cpp_test_agent"}

    requires = (
        "protobuf/3.21.12",
        "up-cpp/0.1.2-dev",
        "rapidjson/cci.20230929",
        "spdlog/1.13.0",
        "fmt/10.2.1",
        "openssl/1.1.1w",
    )

    def source(self):
        # Workaround for compatibility with conan1 and conan2
        # https://github.com/conan-io/conan/issues/13506
        try:
            fork = self.options.fork
            commitish = self.options.commitish
        except AttributeError:
            fork = self.info.options.fork
            commitish = self.info.options.commitish

        git = Git(self)
        git.clone("https://github.com/{}.git".format(fork), target=".")
        git.checkout(commitish)
        # Change to the subdirectory containing the up_client_socket code
        os.chdir("up_client_socket/cpp")
        self.run("git submodule update --init --recursive")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="up_client_socket/cpp")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["up_client_socket"]
