######
## This script processes an RDF graph to find entities that 
## are in contact based on their translations. 
## Then it updates the graph to establish hasCurrentLocation relationships.
######

# Version for kg_base


from rdflib import Graph, Namespace, URIRef
import math
from itertools import combinations
from rdflib import BNode

# Load the RDF graph
g = Graph()
g.parse("kg_base.ttl", format="turtle")  # Replace with your actual file name

# Define the namespace
KORO = Namespace("http://w3id.org/koro#")

'''
# Helper function to convert translation string to float tuple
def parse_translation(translation_str):
    return tuple(map(float, translation_str.strip().split()))
'''

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
        # Look under hasCurrentLocation
        for _, _, trans in g.triples((current_loc_node, KORO.hasTranslation, None)):
            translation_node = trans
            break

    if translation_node is None:
        # Fallback: look directly under hasLocation
        for _, _, trans in g.triples((loc, KORO.hasTranslation, None)):
            translation_node = trans
            break

    if translation_node is None:
        continue  # no translation found anywhere

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
        print(f"⚠️ Missing translation coordinate for {s}")
    else:
        entities.append((s, (x, y, z)))

# Compare each pair
print("Entities in contact:")
for (uri1, t1), (uri2, t2) in combinations(entities, 2):
    if in_contact(t1, t2):
        print(f"- {uri1.split('#')[-1]} and {uri2.split('#')[-1]} are close by.")

# For each pair of object/Kitchen(Storage)Component in contact, add hasCurrentLocation

for (uri1, t1), (uri2, t2) in combinations(entities, 2):
    if in_contact(t1, t2):
        # determine which is Object and which is Furniture
        if KORO.Object in g.objects(uri1, None) and any(cls in g.objects(uri2, None) for cls in [KORO.Appliance, KORO.Storage, KORO.Furnishing]):
            obj, furn = uri1, uri2
        elif any(cls in g.objects(uri1, None) for cls in [KORO.Appliance, KORO.Storage, KORO.Furnishing]) and KORO.Object in g.objects(uri2, None):
            obj, furn = uri2, uri1
        else:
            continue  # not a relevant pair

        # find the hasLocation blank node of the Object
        location_node = None
        for _, _, loc in g.triples((obj, KORO.hasLocation, None)):
            location_node = loc
            break

        if location_node is not None:
            # locate existing hasCurrentLocation within location_node
            current_loc_node = None
            for _, _, cloc in g.triples((location_node, KORO.hasCurrentLocation, None)):
                current_loc_node = cloc
                break

            if current_loc_node is None:
                # if no hasCurrentLocation yet, create one
                current_loc_node = BNode()
                g.add((location_node, KORO.hasCurrentLocation, current_loc_node))

            # find translation node inside hasCurrentLocation
            translation_node = None
            for _, _, trans in g.triples((current_loc_node, KORO.hasTranslation, None)):
                translation_node = trans
                break

            if translation_node is not None:
                # attach furniture as location component at current_loc_node
                g.add((current_loc_node, KORO.hasLocationComponent, furn))

                # optionally: if you want to remove an old LocationComponent or Translation you can do it here
            else:
                print(f"Warning: no hasTranslation found in hasCurrentLocation of {obj}")

        else:
            print(f"Warning: no hasLocation found for {obj}")



### test ###

# all the component types you care about
component_classes = [KORO.Object, KORO.Appliance, KORO.Storage, KORO.Furbishing,KORO.Component]

for s in g.subjects():
    if not any(cls in g.objects(s, None) for cls in component_classes):
        continue

    location_node = None
    for _, _, loc in g.triples((s, KORO.hasLocation, None)):
        location_node = loc
        break

    if location_node is None:
        print(f"Warning: no location found for {s}")
        continue

    # if it already has a hasCurrentLocation, skip it
    if any(True for _ in g.objects(location_node, KORO.hasCurrentLocation)):
        continue  # already processed

    translation_node = None
    for _, _, trans in g.triples((location_node, KORO.hasTranslation, None)):
        translation_node = trans
        break

    if translation_node is None:
        print(f"Warning: no translation found for {s}")
        continue

    current_loc_node = BNode()
    g.add((location_node, KORO.hasCurrentLocation, current_loc_node))
    g.add((current_loc_node, KORO.hasTranslation, translation_node))
    g.remove((location_node, KORO.hasTranslation, translation_node))



# Save the updated graph to a new file
g.serialize(destination="updated_kg_base.ttl", format="turtle")