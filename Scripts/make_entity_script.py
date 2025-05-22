# This script takes entities_annotated.csv as outputed by extract_script.py after it 
# is annotated with an additional colum for the type of entity and generates 
# a turtle file

import sys
import pandas as pd

def make_turtle_entity(nid, name, translation, entity_type):
    entity_uri = f":{name.replace('(', '_').replace(')', '')}"
    lines = []
    if entity_type == "Object":
        lines = [
            f"{entity_uri} a :{entity_type} ;",
            f'    dcterms:identifier "{nid}" ;',
            f'    rdfs:label "{entity_uri}" ;',
            f'    :translation "{translation}" .\n\n'
        ]
    return "\n".join(lines)
    

def main(output_path):
    csv_content = open('./Inputs/entities_annotated.csv')
    df = pd.read_csv(csv_content, header=0)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("@prefix : <http://example.org/entities#> .\n"
                "@prefix dcterms: <http://purl.org/dc/terms/> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")
        for _, row in df.iterrows():
            if pd.notna(row['type']):
                turtle = make_turtle_entity(row['nid'], row['name'], row['translation'], row['type'])
                f.write(turtle)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py output.ttl")
        sys.exit(1)
    main(sys.argv[1])

