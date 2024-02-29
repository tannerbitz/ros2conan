from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import copy
from conan.tools.scm import Version
from sys import version_info

class AmentPackageConan(ConanFile):
    name = "ament_package"
    version = "0.14.0"
    description = """This is ament package's description"""
    license = "Apache"
    author = "Dirk Thomas"
    author_email = "dthomas@osrfoundation.org"
    url = "https://github.com/ament/ament_package/wiki"
    no_copy_source = True

    options = {
        "python_version": ["*", "3.8", "3.9", "3.10", "3.11", "3.12"]
    }

    default_options = {
        "python_version": "*"
    }


    @property
    def py_version_range(self):
        py_version = self.options.python_version
        py_version_range = "[*]"
        if (py_version != "*"):
            py_version_opt = Version(py_version)
            py_major_min_min = Version(f"{py_version_opt.major}.{py_version_opt.minor}")
            py_major_min_max = py_major_min_min.bump(1)
            py_version_range = f"[>={py_major_min_min} <{py_major_min_max}]"
        return py_version_range

    def requirements(self):
        self.requires(f"cpython/{self.py_version_range}")

    def build_requirements(self):
        self.tool_requires(f"cpython/{self.py_version_range}")

    def source(self):
        url = "https://github.com/ament/ament_package.git"
        git = Git(self)
        git.clone(url=url, target=self.source_folder)
        git.folder = self.source_folder
        git.checkout(commit="humble")

    def package(self):
        self.run(f"pip3 install --target={self.package_folder} .", cwd=self.source_folder)
        copy(self, "LICENSE", self.source_folder, self.package_folder)

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)

