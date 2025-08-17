######
## This script processes an RDF graph to find entities that 
## are in contact based on their translations. 
## Then it updates the graph to establish hasCurrentLocation relationships.
######

# Version for kg_annotated
# use: python kg_editor_annotated.py
# output file: final_kg_annotated.ttl

from rdflib import Graph, Namespace, URIRef, BNode
from itertools import combinations
from rdflib.namespace import RDF

# Load the RDF graph
g = Graph()
g.parse("../Inputs/kg_annotated.ttl", format="turtle")  # Replace with your actual file name

# Define the namespace
KORO = Namespace("http://w3id.org/koro#")

# Function to check if two float values are within 10% of each other
def within_10_percent(a, b):
    if a == 0 or b == 0:
         return abs(a - b) < 0.10
    return abs(a - b) / max(abs(a), abs(b)) <= 0.10

# Function to determine if two translations are "in contact"
def in_contact(t1, t2):
    return all(within_10_percent(a, b) for a, b in zip(t1, t2))

# Collect all entities with a translation
entities = []

for s, _, loc in g.triples((None, KORO.hasLocation, None)):
    # Try to find hasCurrentLocation first
    current_loc_node = None
    for _, _, cloc in g.triples((loc, KORO.hasCurrentLocation, None)):
        current_loc_node = cloc
        break

    translation_node = None

    if current_loc_node is not None:
        for _, _, trans in g.triples((current_loc_node, KORO.hasTranslation, None)):
            translation_node = trans
            break

    if translation_node is None:
        for _, _, trans in g.triples((loc, KORO.hasTranslation, None)):
            translation_node = trans
            break

    if translation_node is None:
        continue

    # Extract x, y, z
    x = y = z = None
    for _, p, o in g.triples((translation_node, None, None)):
        if p == KORO.translationX:
            x = float(o)
        elif p == KORO.translationY:
            y = float(o)
        elif p == KORO.translationZ:
            z = float(o)

    if None in (x, y, z):
        print(f"Missing translation coordinate for {s}")
    else:
        entities.append((s, (x, y, z)))

# Compare each pair
print("Entities in contact:")
for (uri1, t1), (uri2, t2) in combinations(entities, 2):
    if in_contact(t1, t2):
        print(f"- {uri1.split('#')[-1]} and {uri2.split('#')[-1]} are close by.")

# For each pair of object/Kitchen(Storage)Component in contact, add hasCurrentLocation
for (uri1, t1), (uri2, t2) in combinations(entities, 2):
    if not in_contact(t1, t2):
        continue

    obj, furn = None, None

    uri1_types = set(g.objects(uri1, RDF.type))
    uri2_types = set(g.objects(uri2, RDF.type))

    uri1_is_object = any(t == KORO.Object for t in uri1_types)
    uri2_is_furniture = any(t in [KORO.Appliance, KORO.Storage, KORO.Furbishing] for t in uri2_types)

    uri2_is_object = any(t == KORO.Object for t in uri2_types)
    uri1_is_furniture = any(t in [KORO.Appliance, KORO.Storage, KORO.Furbishing] for t in uri1_types)

    if uri1_is_object and uri2_is_furniture:
        obj, furn = uri1, uri2
    elif uri2_is_object and uri1_is_furniture:
        obj, furn = uri2, uri1
    else:
        continue

    print(f"🎯 Found Object {obj.split('#')[-1]} and Furniture {furn.split('#')[-1]} in contact")

    if obj == furn:
        continue

    location_node = next(g.objects(obj, KORO.hasLocation), None)
    if not location_node:
        print(f"⚠ No hasLocation for {obj}")
        continue

    current_loc_node = next(g.objects(location_node, KORO.hasCurrentLocation), None)
    if not current_loc_node:
        current_loc_node = BNode()
        g.add((location_node, KORO.hasCurrentLocation, current_loc_node))

        translation_node = next(g.objects(location_node, KORO.hasTranslation), None)
        if translation_node:
            g.remove((location_node, KORO.hasTranslation, translation_node))
            g.add((current_loc_node, KORO.hasTranslation, translation_node))

    existing_components = set(g.objects(current_loc_node, KORO.hasLocationComponent))
    if furn not in existing_components:
        g.add((current_loc_node, KORO.hasLocationComponent, furn))
        print(f"✅ Added: {obj.split('#')[-1]} → hasLocationComponent → {furn.split('#')[-1]}")
    else:
        print(f"ℹ hasLocationComponent already present for {obj.split('#')[-1]}")


# Save the updated graph to a new file
g.serialize(destination="../Outputs/final_kg_annotated.ttl", format="turtle")
