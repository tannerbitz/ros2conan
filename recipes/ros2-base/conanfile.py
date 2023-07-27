# Software License Agreement (BSD License)
#
#  Copyright (c) 2021, iRobot ROS
#  All rights reserved.
#
#  This file is part of conan-ros2, which is released under BSD-3-Clause.
#  You may use, distribute and modify this code under the BSD-3-Clause license.
#

import os
import sys

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import mkdir, replace_in_file, chdir, copy, collect_libs
import yaml

class Ros2Base(object):
    options = {"python_version": "ANY"}
    tools_requires = "vcstool/system", "colcon/system"

    @property
    def _ws_dir(self):
        return "_ws"

    @property
    def _source_dir(self):
        """Default name for the sources directory in a ROS 2 workspace"""
        return "src"

    @property
    def _install_dir(self):
        """Default name for the install directory in a ROS 2 workspace"""
        return "install"

    @property
    def _python_version(self):
        """The currently used Python version as a string"""
        return "python{major}.{minor}".format(major=sys.version_info[0], minor=sys.version_info[1])


    def _create_repo_file(self, repos_path, url=self.url, version=str(self.version)):
        """Creates repos file to representing one repo"""
        repos_contents = { 'repositories' : { 'repo' : { 'type' : 'git', 'url' : url, 'version' : version } } }
        with open(repos_path, 'w') as f:
            yaml.dump(repos_contents, f)

    def _import_repositories(self, source_dir, repos_file, strict=True):
        """
        Given a .repos file, uses vcs tool to import all the repositories into source_dir.
        If the strict flag is set to True, it raises an error if the .repos file is not found.
        """
        if os.path.isfile(repos_file):
            mkdir(self, source_dir)
            self.run("vcs import {src_dir} < {repos_file}".format(src_dir=source_dir , repos_file=repos_file))
        elif strict:
            raise OSError("repository file not found")

    def _colcon_build_ws(self, colcon_args = [], cmake_args = []):
        """
        Builds a ROS 2 workspace using the colcon build tool. The provided CMake arguments are added
        to some default colcon arguments.
        """
        colcon_args += [
            "--merge-install",
            "--cmake-force-configure",
        ]

        if cmake_args:
            cmake_args_string = ' '.join(cmake_args)
            colcon_args.append("--cmake-args {args}".format(args=cmake_args_string))

        colcon_args_string = ' '.join(colcon_args)

        # Run the colcon command inside the workspace directory
        with chdir(self, os.path.join(self.build_folder, self._ws_dir):
            self.run("colcon build {args}".format(args=colcon_args_string))

    def _colcon_build(self, cmake_args = []):
        """
        Builds a ROS 2 workspace using the colcon build tool. The provided CMake arguments are added
        to some default colcon arguments.
        """
        self._colcon_build_ws(['--packages-select', self.name], cmake_args)

    def _replace_python_shebangs(self, python_scripts_dir, python_version):
        """
        Replaces the Python shebang that Setuptools adds to Python scripts entry points, as that one may use
        the absolute paths and this makes the scripts non-relocatable.
        Several discussions on the web, e.g. https://stackoverflow.com/questions/1530702/dont-touch-my-shebang 
        """
        virtual_env_shebang = "#!{python_executable}".format(python_executable=sys.executable)
        absolute_path_shebang = "#!/usr/bin/python3"
        generic_python_shebang = "#!/usr/bin/env {python_version}".format(python_version=python_version)
        if os.path.isdir(python_scripts_dir):
            for filename in os.listdir(python_scripts_dir):
                filepath = os.path.join(python_scripts_dir, filename)
                replace_in_file(self, filepath, virtual_env_shebang, generic_python_shebang, strict=False)
                replace_in_file(self, filepath, absolute_path_shebang, generic_python_shebang, strict=False)

    def configure(self):
        # The ROS 2 packages contains some python3 modules that are only compatible with the python version used to create the package.
        # We add this dummy Conan option to encode the supported python version on the package metadata.
        if self.options.python_version and self.options.python_version != self._python_version:
            raise ConanInvalidConfiguration("Do not set Python version option, Conan will automatically detect the one used to build the package")
        self.options.python_version = self._python_version

    def package(self):
        install_dir_path = os.path.join(self.build_folder, self._ws_dir, self._install_dir)

        # Post build patch
        ros2_bin_dir = os.path.join(install_dir_path, "bin")
        self._replace_python_shebangs(ros2_bin_dir, self._python_version)

        copy(self, "*", dst=self.package_folder , src=install_dir_path)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        self.buildenv_info.prepend_path("AMENT_PREFIX_PATH", self.package_folder)
        self.buildenv_info.prepend_path("CMAKE_PREFIX_PATH", self.package_folder)
        self.buildenv_info.prepend_path("COLCON_PREFIX_PATH", self.package_folder)

        self.runenv_info.prepend_path("AMENT_PREFIX_PATH", self.package_folder)

        python_dir = os.path.join(self.package_folder, "lib", self._python_version, "site-packages")
        if os.path.isdir(python_dir):
            self.buildenv_info.prepend_path("PYTHONPATH", python_dir)
            self.runenv_info.prepend_path("PYTHONPATH", python_dir)

class Ros2BaseReq(ConanFile):
    name = "ros2-base"
    version = "0.0.1"
    license = "Apache 2.0"
    url = "https://index.ros.org/doc/ros2/"
    homepage = "https://index.ros.org/doc/ros2/"
    description = "Python requires for ROS 2 conan recipes"
