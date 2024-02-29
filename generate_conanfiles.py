#!/usr/bin/env python3

import yaml
import os
import glob
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rospackageparser import *
from dataclasses import asdict
import json
from os import PathLike
from typing import Union


def render(metadata: PackageMetadata, deps: ConanDeps):
    env = Environment(
        loader=FileSystemLoader("templates")
    )
    template = env.get_template("cmake_conanfile.jinja")

    args = {'name': "Tanner Bitz" }
    all_deps = asdict(deps)
    conan_reqs = all_deps['requires']
    conan_build_requirements = all_deps['build_requirements']
    print(template.render(requirements=conan_reqs,
                          build_requirements=conan_build_requirements,
                          **asdict(metadata)))

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


if __name__ == "__main__":
    repos = read_repos("ros2.repos")

    pkg_metadatas = {}
    for repo in repos["repositories"]:
        pkg_xmls = get_repo_packages("src", repo)
        for pkg_xml in pkg_xmls:
            pkg_xml_path = os.path.join("src", repo, pkg_xml)
            pkg_meta = package_metadata(pkg_xml_path)
            pkg_metadatas[pkg_meta.name] = pkg_meta

    src_dir = Path(__file__).parent.absolute() / "src"
    package_xmls = get_package_xml_files(src_dir)

    package = Path(src_dir, package_xmls[20])
    print(package)
    metadata, deps = parse_package(package)

    conan_deps = convert_to_conandeps(deps, pkg_metadatas)
    render(metadata, conan_deps)


