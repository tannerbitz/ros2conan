#!/usr/bin/env python3

import yaml
import os
import glob
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def render():
    env = Environment(
        loader=FileSystemLoader("templates")
    )
    template = env.get_template("cmake_conanfile.jinja")

    args = {'name': "Tanner Bitz", 'author': 'low' }
    print(template.render(**args))


def read_repos(repos_file: str) -> dict:
    is_file = os.path.isfile(repos_file)
    if (not is_file):
        return {}

    with open(repos_file, 'r') as file:
        repos = yaml.safe_load(file)
        return repos


def get_package_xml_files(root_path):
    return glob.glob("**/package.xml", root_dir=root_path, recursive=True)


def has_file(dirname, fname):
    return os.path.isfile(os.path.join(dirname, fname))


def has_cmakelists(dirname):
    return has_file(dirname, "CMakeLists.txt")


def has_setup_py(dirname):
    return has_file(dirname, "setup.py")


if __name__ == "__main__":
    # repos = read_repos("ros2.repos")

    # src_dir = Path(__file__).parent.absolute() / "src"
    # package_xmls = get_package_xml_files(src_dir)
    # print(package_xmls)

    render()
