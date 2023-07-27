from conan import ConanFile
from conan.tools.system import package_manager

required_conan_version = ">=1.51.3"


class VCSToolConan(ConanFile):
    name = "vcstool"
    version = "system"
    description = "cross-platform virtual conan package for vcstool"
    topics = ("vcstool")
    author = "Dirk Thomas <web@dirk-thomas.net>"
    url = "https://github.com/dirk-thomas/vcstool"
    license = "Apache-2.0"
    package_type = "application"
    settings = "os"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["python3-vcstool"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["python3-vcstool"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["python3-vcstool"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["python3-vcstool"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["python3-vcstool"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["python3-vcstool"], update=True, check=True)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
