# Software License Agreement (BSD License)
#
#  Copyright (c) 2021, iRobot ROS
#  All rights reserved.
#
#  This file is part of conan-ros2, which is released under BSD-3-Clause.
#  You may use, distribute and modify this code under the BSD-3-Clause license.
#

import os
from conan import ConanFile

class AmentPackageConan(ConanFile):
    name = "ament_package"
    license = "Apache 2.0"
    url = "https://github.com/ament/ament_package"

    python_requires = "ros2-base/0.0.1"
    python_requires_extend = "ros2-base.Ros2Base"

    def layout(self):
        self.folders.source = "src"
        self.folders.build = ""
        self.folders.generators = "generators"

    def source(self):
        repos_file_path = os.path.join(self.source_folder, f'{self.name}.repos')
        self._create_repo_file(repos_file_path, self.url, str(self.version))

        self._import_repositories(".", repos_file_path)

    def build(self):
        # Invoke colcon on the workspace
        self._colcon_build()
