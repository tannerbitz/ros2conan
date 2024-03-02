#!/usr/bin/env python3

import yaml
from os import PathLike
import os
import glob
from typing import Union

def read_repos(repos_file: str) -> dict:
    is_file = os.path.isfile(repos_file)
    if (not is_file):
        return {}

    with open(repos_file, 'r') as file:
        repos = yaml.safe_load(file)
        return repos

def get_repo_packages(root_path: PathLike, repo_dir: PathLike) -> list[str]:
    return get_package_xml_files(os.path.join(root_path, repo_dir))

def get_package_xml_files(root_path) -> list[str]:
    return glob.glob("**/package.xml", root_dir=root_path, recursive=True)


def has_file(dirname: PathLike, fname: Union[PathLike, str]) -> bool:
    return os.path.isfile(os.path.join(dirname, fname))


def has_cmakelists(dirname: PathLike) -> bool:
    return has_file(dirname, "CMakeLists.txt")

def has_setup_py(dirname: PathLike) -> bool:
    return has_file(dirname, "setup.py")



