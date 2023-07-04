import xml.etree.ElementTree as ET
import copy
from dataclasses import dataclass
from typing import List
import logging


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

def package_metadata(package):
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
class DependencyInfo:
    build_depend: bool = False
    build_export_depend: bool = False
    buildtool_depend: bool = False
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


def get_dependencies(package):
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
        "exec_depend" ,
        "depend" ,
        "doc_depend",
        "test_depend" ,
        "conflict",
        "replace",
    ]

    dependencies = {str(child.text): DependencyInfo() for child in root if child.tag in dependency_tag_names}

    for child in root:
        if child.tag in dependency_tag_names:
            if child.tag == "build_depend":
                dependencies[str(child.text)].build_depend = True
            elif child.tag == "build_export_depend":
                dependencies[str(child.text)].build_export_depend = True
            elif child.tag == "buildtool_depend":
                dependencies[str(child.text)].buildtool_depend = True
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

def parse_package(package):
    if not os.path.isfile(package):
        logging.warn(f"{package} is not a file. Skipping package parse")
        return None

    metadata = package_metadata(package)
    if metadata is None:
        logging.warn(f"Failed to get package metadata from {package}")
        return None

    deps_map = get_dependencies(package)

    return (metadata,deps_map)


if __name__ == "__main__":
    import glob
    import os
    packages = glob.glob('**/package.xml', root_dir=os.path.dirname(__file__), recursive=True)

    non_ignored_packages = list(filter(lambda x: not glob.glob("*_IGNORE", root_dir=os.path.dirname(x)), packages))
    packages_with_build_type = list(filter(lambda x: get_build_types(x), non_ignored_packages))

    deps = get_dependencies(packages_with_build_type[-1])
    for dep, dep_info in deps.items():
        print("\n{}\n\t{}".format(dep, dep_info))



