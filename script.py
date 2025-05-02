############################################################
# This script will extract data from kitchen_simulation.py #
# and later create a knowledge graph using rdflib.         #
############################################################

import rdflib
import re # Regular expression module





############################## knowledge graph creation ##############################

# Create a new RDF graph
graph = rdflib.Graph()

# Example: Add a triple to the graph
subject = rdflib.URIRef("http://example.org/subject")
predicate = rdflib.URIRef("http://example.org/predicate")
obj = rdflib.Literal("Object")

graph.add((subject, predicate, obj))

# Print all triples in the graph
for s, p, o in graph:
    print(f"Subject: {s}, Predicate: {p}, Object: {o}")