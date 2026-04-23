from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy
from conan.tools.scm import Git
import os


class UringExecConan(ConanFile):
    name = "uring_exec"
    package_type = "header-library"
    license = "MIT"
    url = "https://github.com/hollykbuck/uring_exec"
    description = "io_uring support for stdexec/std::execution"
    topics = ("io-uring", "stdexec", "execution", "async")

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "include/*", "LICENSE", "README.md"
    no_copy_source = True

    def set_version(self):
        git = Git(self, self.recipe_folder)
        try:
            self.version = git.run("rev-parse --short HEAD").strip()
        except Exception:
            self.version = "0.1.0"

    def requirements(self):
        self.requires("stdexec/2026.4.0")
        self.requires("liburing/2.13")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if str(self.settings.os) != "Linux":
            raise ConanInvalidConfiguration("uring_exec requires Linux because it depends on io_uring")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, "20")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        include_src = os.path.join(self.source_folder, "include")
        copy(self, "*.hpp", include_src, os.path.join(self.package_folder, "include"))
        copy(self, "*.h", include_src, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "uring_exec")
        self.cpp_info.set_property("cmake_target_name", "uring_exec::uring_exec")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.system_libs.append("pthread")
