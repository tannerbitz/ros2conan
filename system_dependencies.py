#!/usr/bin/env python3

from typing import Generator
import subprocess
from utils import *
from rospackageparser import *
from dataclasses import dataclass, asdict
import json

def run_rosdep_resolve_on_deps(deps: list[str]) -> str:
    result = subprocess.run(["rosdep", "resolve"] + deps, capture_output=True, text=True)
    return result.stdout

def ros_dep_resolve_lexer(ros_dep_resolve_output: str) -> Generator[str, None, None]:
    seperators = ["\n", " ", "[", "]"]

    current_token = ''
    for char in ros_dep_resolve_output:
        if char in seperators:
            if current_token:
                yield current_token
                current_token = ''
        else:
            current_token += char

@dataclass
class SystemDep:
    name: str = ""
    system_libs: list[str] = field(default_factory=list)
    replace_with: str = ""

def parser(tokens: Generator[str, None, None]) -> list[SystemDep]:

    start_token = "#ROSDEP"

    system_deps: list[SystemDep] = []
    dep = SystemDep()
    for token in tokens:
        if token == start_token:
            if dep.name and dep.system_libs:
                system_deps.append(dep)
            dep = SystemDep()
        elif token.startswith("#"):
            continue
        else:
            if not dep.name:
                dep.name = token
            else:
                dep.system_libs.append(token)

    return system_deps


def get_system_libraries(deps: list[str]) -> list[SystemDep]:
    result = subprocess.run(["rosdep", "resolve"] + deps, capture_output=True, text=True)

    tokens = ros_dep_resolve_lexer(result.stdout)
    system_libs = parser(tokens)
    return system_libs

if __name__ == "__main__":
    repos = read_repos("ros2.repos")

    all_deps = []
    pkg_metadatas = {}
    for repo in repos["repositories"]:
        pkg_xmls = get_repo_packages("src", repo)
        for pkg_xml in pkg_xmls:
            pkg_xml_path = os.path.join("src", repo, pkg_xml)
            pkg_meta = package_metadata(pkg_xml_path)
            pkg_metadatas[pkg_meta.name] = pkg_meta

            deps = get_dependencies(pkg_xml_path)
            for dep, _ in deps.items():
                all_deps.append(dep)

    skipped_keys = ["python-catkin-pkg"]
    all_deps = list(set(all_deps))
    deps = [x for x in all_deps if x not in skipped_keys]
    system_libs = get_system_libraries(deps)

    system_libs = [asdict(dep) for dep in system_libs]
    with open("system_libraries.json", "w") as json_file:
        json.dump(system_libs, json_file, indent=2)
    
