import xml.etree.ElementTree as ET
import os

def parse_package(pkg_file):
    if not os.path.isfile(pkg_file):
        return {}
    
    tree = ET.parse(pkg_file)
    root = tree.getroot()
    
