from conan import ConanFile
from conan.tools.system import package_manager

required_conan_version = ">=1.51.3"


class ColconConan(ConanFile):
    name = "colcon"
    version = "system"
    description = "cross-platform virtual conan package for colcon"
    topics = ("colcon")
    author = "Dirk Thomas <web@dirk-thomas.net>"
    url= "https://github.com/colcon/colcon-core"
    license = "Apache-2.0"
    package_type = "application"
    description = "Meta package aggregating colcon-core and common extensions"
    settings = "os"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["python3-colcon-common-extensions"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["python3-colcon-common-extensions"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["python3-colcon-common-extensions"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["python3-colcon-common-extensions"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["python3-colcon-common-extensions"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["python3-colcon-common-extensions"], update=True, check=True)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
