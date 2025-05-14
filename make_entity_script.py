# This script takes an xlsx file as outputed by extract_script.py after it is annotated
# with an additional colum for the type of entity and generates a turtle file

import sys
import pandas as pd

def make_turtle_entity(nid, name, translation, entity_type):
    entity_uri = f":{name.replace(' ', '_')}"
    lines = [
        f"{entity_uri} a :{entity_type} ;",
        f'    :nid "{nid}" ;',
        f'    :name "{name}" ;',
        f'    :translation "{translation}" .\n'
    ]
    return "\n".join(lines)
    

def main(xlsx_path, output_path):
    df = pd.read_excel(xlsx_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("@prefix : <http://example.org/entities#> .\n\n")
        for _, row in df.iterrows():
            if pd.notna(row['type']):
                turtle = make_turtle_entity(row['nid'], row['name'], row['translation'], row['type'])
                f.write(turtle)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.xlsx output.ttl")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

