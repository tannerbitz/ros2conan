#!/usr/bin/env python3

import yaml
from os import PathLike
import os
import glob
from typing import Union
from pathlib import Path
from dataclasses import dataclass, asdict
import json

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

def has_setup_cfg(dirname: PathLike) -> bool:
    return has_file(dirname, "setup.cfg")

def has_colcon_ignore(dirname: PathLike) -> bool:
    return has_file(dirname, "COLCON_IGNORE")

@dataclass
class PkgTypeMeta:
    setup_py: bool = False
    setup_cfg: bool = False
    cmakelists: bool = False
    ignore: bool = False

    def __init__(self, pkg_root):
        self.setup_py = has_setup_py(pkg_root)
        self.setup_cfg = has_setup_cfg(pkg_root)
        self.cmakelists = has_cmakelists(pkg_root)
        self.ignore = has_colcon_ignore(pkg_root)

    def is_python_pkg(self):
        return self.setup_cfg or self.setup_py

    def is_cpp_pkg(self):
        return self.cmakelists

if __name__ == "__main__":
    dir = Path(__file__).parent
    pkgs = get_repo_packages(dir, "src")

    pkg_type_metas = {}
    for pkg in pkgs:
        pkg_xml = os.path.join(dir, "src", pkg)
        pkg_dir = Path(pkg_xml).parent

        pkg_name = pkg_dir.name
        pkg_type_metas[pkg_name] = PkgTypeMeta(pkg_dir)

    python_and_cpp_pkgs = { k:asdict(v) for k,v in pkg_type_metas.items() if v.is_python_pkg() and v.is_cpp_pkg() }
    print(json.dumps(python_and_cpp_pkgs, indent=2))

    




