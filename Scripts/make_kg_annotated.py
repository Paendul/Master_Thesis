# This script takes entities_annotated.csv as outputed by extract_script.py after it 
# is annotated with an additional colum for the type of entity and generates 
# a turtle file

# Version for kg_annotated

# USAGE: python3 make_entity_script.py output.ttl
# Practical output file name: kg_annotated.ttl

import sys
import pandas as pd
import re
import os

def make_turtle_entity(nid, name, translation, entity_type, target, translation_lookup):
    entity_uri = f":{name.replace('(', '_').replace(')', '')}"
    cleaned_label = re.sub(r'\d+', '', entity_uri.replace(":", "").replace("_", ""))
    translations = translation.split()

    lines = [
        f'koro{entity_uri.replace(" ","_")} a koro:{entity_type} ;',
        f'    dcterms:identifier "{nid}" ;',
        f'    rdfs:label "{entity_uri.replace(":","").replace("_", " ")}" ;',
        f'    bbccore:preferredLabel "{cleaned_label}" ;',
        f'    koro:hasLocation [',
        f'      koro:hasCurrentLocation [',
        f'          koro:hasTranslation [',
        f'              koro:translationX {translations[0]} ;',
        f'              koro:translationY {translations[1]} ;',
        f'              koro:translationZ {translations[2]} ] ]'
    ]

    # only add hasTargetLocation if target is not empty/NaN
    if pd.notna(target) and target in translation_lookup:
        target_translations = translation_lookup[target].split()
        lines.extend([
            f'    ;',
            f'      koro:hasTargetLocation [',
            f'          koro:hasLocationComponent koro:{target.replace(" ", "_")} ;',
            f'          koro:hasTranslation [',
            f'              koro:translationX {target_translations[0]} ;',
            f'              koro:translationY {target_translations[1]} ;',
            f'              koro:translationZ {target_translations[2]} ] ]'
        ])

    # close the Location and the whole block
    lines.append('    ] .\n\n')
    return "\n".join(lines)


def main(output_path):
    df = pd.read_csv('../Inputs/entities_annotated.csv', header=0)

    # build a lookup of name -> translation
    translation_lookup = {}
    for _, row in df.iterrows():
        if pd.notna(row['name']) and pd.notna(row['translation']):
            translation_lookup[row['name']] = row['translation']

    # Ensure output_path is just the filename, not a full path
    output_filename = os.path.basename(output_path)
    output_full_path = os.path.join('../Inputs/', output_filename)

    with open(output_full_path, "w", encoding="utf-8") as f:
        f.write(
            "@prefix koro: <http://w3id.org/koro#> .\n"
            "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
            "@prefix dcterms: <http://purl.org/dc/terms/> .\n"
            "@prefix bbccore: <http://www.bbc.co.uk/ontologies/coreconcepts/> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n"
        )

        for _, row in df.iterrows():
            if pd.notna(row['type']):
                turtle = make_turtle_entity(
                    row['nid'], row['name'], row['translation'],
                    row['type'], row.get('target', None), translation_lookup
                )
                f.write(turtle)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py output.ttl")
        sys.exit(1)
    main(sys.argv[1])
