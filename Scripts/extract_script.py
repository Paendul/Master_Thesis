# This script extracts the id, name, and translation attributes
# from Solid elements in a W3D file and saves them to an Excel file.
# Use: python extract_script.py

import xml.etree.ElementTree as ET
import pandas as pd

def extract_solid_names_and_translations(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    results = []
    for solid in root.findall(".//Solid"):
        nid = solid.get("id")
        name = solid.get("name")
        translation = solid.get("translation")
        if name is not None and translation is not None and nid is not None:
            results.append({"nid": nid, "name": name, "translation": translation, "type": None})
    return results


def save_results_to_csv(results, filename):
    df = pd.DataFrame(results)
    df.to_csv(f'./Inputs/{filename}', index=False)

xml_content = open('./Inputs/kitchen_simulation.w3d').read()
results = extract_solid_names_and_translations(xml_content)
save_results_to_csv(results, 'entities.csv')

