from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
import os

class TestAgentRecipe(ConanFile):
    name = "test_agent_cpp"
    package_type = "executable"
    license = "Apache-2.0 license"
    homepage = "https://github.com/eclipse-uprotocol"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ Test Agent"
    #topics = ("ulink client", "transport")
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    conan_version = None
    generators = "CMakeDeps"
    version = "0.1"
    exports_sources = "CMakeLists.txt", "src/*" 

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_cross_compiling": [True, False],
        "build_testing": [True, False],
        "build_unbundled": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": False,
        "build_cross_compiling": True,
        "build_testing": False,
        "build_unbundled": False,
    }

    def configure(self):
        self.options["libuuid"].shared = True
        
    def requirements(self):
        self.requires("protobuf/3.21.12")
        self.requires("up-cpp/0.1.5.0-dev")
        self.requires("rapidjson/cci.20230929")
        self.requires("spdlog/1.13.0")
        self.requires("fmt/10.2.1")
        self.requires("libuuid/1.0.3")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def imports(self):
        if self.options.build_testing:
            self.copy("*.so*", dst="lib", keep_path=False)
