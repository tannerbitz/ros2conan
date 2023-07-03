import xml.etree.ElementTree as ET
import os
import copy

def parse_package(pkg_file):
    if not os.path.isfile(pkg_file):
        return {}
    
    tree = ET.parse(pkg_file)
    root = tree.getroot()
    
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

    dependency_tags = {
        "build_depend" : False,
        "build_export_depend" : False,
        "buildtool_depend": False,
        "exec_depend" : False,
        "depend" : False,
        "doc_depend": False,
        "test_depend" : False,
        "conflict": False, # probably inactionble data - very very rarely used
        "replace": False,  # probably inactionble data - very very rarely used
    }

    dependency_tag_names = dependency_tags.keys()

    dependencies = {child.text: copy.deepcopy(dependency_tags) for child in root if child.tag in dependency_tag_names}

    for child in root:
        if child.tag in dependency_tag_names:
            dependencies[child.text][child.tag] = True

    return dependencies

def get_build_types(package):
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
        build_types = [child.text for child in export_element if child.tag == "build_type"]
    
    return build_types