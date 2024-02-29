import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict
import logging
import os
from os import PathLike
from typing import Tuple

@dataclass
class Maintainer:
    name: str
    email: str

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"

@dataclass
class PackageMetadata:
    name: str
    version: str
    description: str
    maintainers: List['Maintainer']
    license: list[str]
    url: list[str]

def package_metadata(package) -> PackageMetadata|None:
    """
    Gather required tags as defined in https://ros.org/reps/rep-0149.html#required-tags
    Required Tags
        The required tags in a package.xml file provide package meta-data:

        <name>
        <version>
        <description>
        <maintainer> (multiple, but at least one)
        <license> (multiple, but at least one)
    """
    tree = ET.parse(package)
    root = tree.getroot()

    name_element        = root.find('name')
    version_element     = root.find('version')
    description_element = root.find('description')
    license_elements    = root.findall('license')
    maintainer_elements = root.findall('maintainer')
    url_elements        = root.findall('url')

    # required elements not found
    if (name_element        is None) or \
       (version_element     is None) or \
       (description_element is None) or \
       (not license_elements)        or \
       (not maintainer_elements):
        logging.warning(f"{package} was missing a required tag")
        return None

    logging.info(f"{package} had all required tags")

    package_meta = PackageMetadata(
        name=str(name_element.text),
        version=str(version_element.text),
        description=str(description_element.text),
        license= [str(license_element.text) for license_element in license_elements],
        maintainers=[Maintainer(name=str(maintainer_el.text), email=maintainer_el.attrib['email']) for maintainer_el in maintainer_elements],
        url=[str(url_element.text) for url_element in url_elements]
    )
 
    return package_meta

@dataclass
class RosDepDescription:
    build_depend: bool = False
    build_export_depend: bool = False
    buildtool_depend: bool = False
    buildtool_export_depend: bool = False
    exec_depend: bool = False
    depend: bool = False
    doc_depend: bool = False
    test_depend: bool = False
    conflict: bool = False
    replace: bool = False
    version_lt: str|None = None
    version_lte: str|None = None
    version_eq: str|None = None
    version_gte: str|None = None
    version_gt: str|None = None


def get_dependencies(package) -> Dict[str, RosDepDescription]:
    """
    Gather data from export section of package.xml as defined by the spec https://ros.org/reps/rep-0149.html#dependency-tags
    Dependency tags
        <build_depend> (multiple)
            Attributes
        <build_export_depend> (multiple)
            Attributes
        <buildtool_depend> (multiple)
            Attributes
        <buildtool_export_depend> (multiple)
            Attributes
        <exec_depend> (multiple)
            Attributes
        <depend> (multiple)
            Attributes
        <doc_depend> (multiple)
            Attributes
        <test_depend> (multiple)
            Attributes
        <conflict> (multiple)
            Attributes
        <replace> (multiple)
            Attributes
    """
    tree = ET.parse(package)
    root = tree.getroot()

    dependency_tag_names = [
        "build_depend" ,
        "build_export_depend" ,
        "buildtool_depend",
        "buildtool_export_depend",
        "exec_depend" ,
        "depend" ,
        "doc_depend",
        "test_depend" ,
        "conflict",
        "replace",
    ]

    dependencies = {str(child.text): RosDepDescription() for child in root if child.tag in dependency_tag_names}

    for child in root:
        if child.tag in dependency_tag_names:
            if child.tag == "build_depend":
                dependencies[str(child.text)].build_depend = True
            elif child.tag == "build_export_depend":
                dependencies[str(child.text)].build_export_depend = True
            elif child.tag == "buildtool_depend":
                dependencies[str(child.text)].buildtool_depend = True
            elif child.tag == "buildtool_export_depend":
                dependencies[str(child.text)].buildtool_export_depend = True
            elif child.tag == "exec_depend":
                dependencies[str(child.text)].exec_depend = True
            elif child.tag == "depend":
                dependencies[str(child.text)].depend = True
            elif child.tag == "doc_depend":
                dependencies[str(child.text)].doc_depend = True
            elif child.tag == "test_depend":
                dependencies[str(child.text)].test_depend = True
            elif child.tag == "conflict":
                dependencies[str(child.text)].conflict = True
            elif child.tag == "replace":
                dependencies[str(child.text)].replace = True

            for attrib, val in child.attrib:
                if attrib in "version_lt":
                    dependencies[str(child.text)].version_lt = val
                elif attrib in "version_lte":
                    dependencies[str(child.text)].version_lte = val
                elif attrib in "version_eq":
                    dependencies[str(child.text)].version_eq = val
                elif attrib in "version_gte":
                    dependencies[str(child.text)].version_gte = val
                elif attrib in "version_gt":
                    dependencies[str(child.text)].version_gt = val

    return dependencies

def get_build_types(package) -> list[str]:
    """ 
    Gather build types from export section of package.xml as defined by the spec https://ros.org/reps/rep-0149.html#export
    <export>
        <architecture_independent/>
        <build_type> (multiple)
            Attributes
        <deprecated>
        <message_generator>
        <metapackage/>  - very very rarely used
    """

    tree = ET.parse(package)
    root = tree.getroot()

    build_types = []

    export_element = root.find('export')
    if export_element is not None:
        build_types = [str(child.text) for child in export_element if child.tag == "build_type"]
    
    return build_types

def parse_package(package: PathLike):
    if not os.path.isfile(package):
        logging.warn(f"{package} is not a file. Skipping package parse")
        return None

    metadata = package_metadata(package)
    if metadata is None:
        logging.warn(f"Failed to get package metadata from {package}")
        return None

    deps_map = get_dependencies(package)

    return (metadata,deps_map)


@dataclass
class ConanRequirement:
    name: str = ""
    version: str = ""
    transitive_headers: bool|None = None
    transitive_libs: bool|None = None

@dataclass
class ConanBuildRequirements:
    tool_requires: list[ConanRequirement] = field(default_factory=list)
    test_requires: list[ConanRequirement] = field(default_factory=list)

@dataclass
class ConanDeps:
    requires: list[ConanRequirement] = field(default_factory=list)
    build_requirements: ConanBuildRequirements = field(default_factory=ConanBuildRequirements)

def get_version_str(dep_name: str, dep_desc: RosDepDescription, pkgs: dict[str, PackageMetadata]) -> str:
    version_str = ""
    has_version_restriction = bool((dep_desc.version_lt  is not None) or
                                   (dep_desc.version_eq  is not None) or
                                   (dep_desc.version_gt  is not None) or 
                                   (dep_desc.version_lte is not None) or
                                   (dep_desc.version_gte is not None))
    
    if has_version_restriction:
        if (dep_desc.version_eq is not None):
            return str(dep_desc.version_eq)
        if (dep_desc.version_lt is not None):
            version_str += f"<{dep_desc.version_lt}"
        if (dep_desc.version_lte is not None):
            version_str += f"<={dep_desc.version_lte}"
        if (dep_desc.version_gt is not None):
            version_str += f">{dep_desc.version_gt}"
        if (dep_desc.version_gte is not None):
            version_str += f">={dep_desc.version_gte}"
    else:
        # impose current version of package as minimum
        try:
            dep_meta = pkgs[dep_name]
            version_str += f">={dep_meta.version}"
        except KeyError:
            return "*"

    return f"[{version_str}]"

def convert_to_conandeps(pkg_ros_deps: dict[str, RosDepDescription], pkgs: dict[str, PackageMetadata]) -> ConanDeps:
    conan_deps = ConanDeps()
    for dep_name, ros_deps in pkg_ros_deps.items():
        version_str = get_version_str(dep_name, ros_deps, pkgs)
        conan_req = ConanRequirement(dep_name, version_str)
        # define requirements traits
        if ros_deps.build_export_depend or ros_deps.depend:
            conan_req.transitive_headers = True
            conan_req.transitive_libs = True
        # place into conan requirements
        if ( ros_deps.build_export_depend or
             ros_deps.build_depend or
             ros_deps.exec_depend or
             ros_deps.depend ):
            conan_deps.requires.append(conan_req)
        if ( ros_deps.buildtool_depend or ros_deps.buildtool_export_depend or ros_deps.doc_depend):
            conan_deps.build_requirements.tool_requires.append(conan_req)
        if ( ros_deps.test_depend ):
            conan_deps.build_requirements.test_requires.append(conan_req)
    return conan_deps

if __name__ == "__main__":
    import glob
    import os
    packages = glob.glob('**/package.xml', root_dir=os.path.dirname(__file__), recursive=True)
    print(f"{len(packages)} packages found")

    package_has_ignore_file = lambda package_xml: glob.glob("*_IGNORE", root_dir=os.path.dirname(package_xml))
    package_without_ignore_file = lambda package_xml: not package_has_ignore_file(package_xml)

    non_ignored_packages = list(filter(package_without_ignore_file, packages))
    print(f"{len(non_ignored_packages)} packages without *_IGNORE")

    packages_with_build_type = list(filter(lambda x: get_build_types(x), non_ignored_packages))
    print(f"{len(packages_with_build_type)} packages without *_IGNORE and with defined build_type")

    ignored_packages = list(filter(package_has_ignore_file, packages))
    print(f"ignored packages: {ignored_packages}")

    deps = get_dependencies(packages_with_build_type[-1])
    for dep, dep_info in deps.items():
        print("\n{}\n\t{}".format(dep, dep_info))



