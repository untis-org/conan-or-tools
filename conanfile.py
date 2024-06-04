import fnmatch
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, update_conandata
import conans.tools as tools
from os.path import join
from conan.tools.files import copy
from collect_ordered_linux_libs import collect_ordered_linux_libs
from conan.tools.scm import Git


class ORToolsConan(ConanFile):
    name = "ortools"
    license = "MIT license"
    url = "https://github.com/google/or-tools/"
    description = "Google Optimization Tools"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports = "collect_ordered_linux_libs.py"
    exports_sources = "or-tools/*", "patches/*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def set_version(self):
        git = Git(self)
        tag = git.run("describe --tags")
        self.version = tag

    def layout(self):
        cmake_layout(self, src_folder="or-tools")

    def source(self):
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_SAMPLES"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DEPS"] = True

        if self.settings.os == "Windows" and self.settings.get_safe("build_type") == "Debug":
            tc.variables["CONAN_CXX_FLAGS"] = "-FS"

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.defines.append(
            "NOMINMAX"
        )  # in eigen is a macro definition for max(x,y) and min(x,y), we disable it

        if (
            self.settings.os == "Linux"
        ):  # on linux the link order is important, therefore we determine the correct order with this helper script
            self.cpp_info.libs = collect_ordered_linux_libs(
                join(self.package_folder, "lib")
            )
        else:  # self.settings.os == "Windows"
            self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
