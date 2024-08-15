# Always prefer setuptools over distutils
from setuptools import find_packages, setup

import os
from os import path
from typing import List

root_dir= path.abspath(path.dirname(__file__))

def load_version() -> str:
    version: str = ""
    with open(os.path.join(root_dir, "version", "VERSION")) as f:
        version = f.read()
    return version

def load_requirements(filename: str) -> List[str]:
    requirements = []
    with open(filename, "rt") as req_file:
        for line in req_file.read().splitlines():
            if not line.strip().startswith("#"):
                requirements.append(line)
    return requirements

project_requirements = load_requirements(os.path.join(root_dir, "requirements.txt"))
dev_requirements = load_requirements(os.path.join(root_dir, "dev_requirements.txt"))

setup(
    name='ros2conan',
    python_requires='>=3.6',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=load_version(),  # + ".rc1",

    description='Conan C/C++ package manager',

    # The project's main homepage.
    url='https://github.com/tannerbitz/ros2conan',

    # Author details
    author='Tanner Bitz',
    author_email='tannerbitz@gmail.com',

    # Choose your license
    license='MIT',

    # What does your project relate to?
    keywords=['C/C++', 'packaging', 'ros2', 'c', 'c++', 'cpp'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=project_requirements,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e ".[dev,test,runners]"
    extras_require={
        'dev': dev_requirements,
        'test': dev_requirements,
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'ros2conan=ros2conan.main:main',
        ],
    },
)
