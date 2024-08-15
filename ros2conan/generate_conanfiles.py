#!/usr/bin/env python3

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rospackageparser import *
from dataclasses import asdict
from utils import *
from system_dependencies import *

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
    get_system_libraries(deps)

    src_dir = Path(__file__).parent.absolute() / "src"
    package_xmls = get_package_xml_files(src_dir)

    package = Path(src_dir, package_xmls[20])
    metadata, deps = parse_package(package)

    conan_deps = convert_to_conandeps(deps, pkg_metadatas)
    # render(metadata, conan_deps)


