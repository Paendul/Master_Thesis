# This script contains test queries for competency questions

from rdflib import Graph, Namespace

# Load your ontology
g = Graph()
g.parse("../Outputs/final_kg_base.ttl", format="turtle")

# Define namespace
koro = Namespace("http://w3id.org/koro#")

query = """PREFIX koro: <http://w3id.org/koro#>
SELECT ?object ?current ?target
WHERE {
    ?object koro:hasCurrentLocation ?current ;
    koro:hasTargetLocation ?target .
    FILTER (?current != ?target)
}"""

results = g.query(query)

print("Objects with different current and target locations:")
for row in results:
    print(f"Object: {row.object}")

query = """PREFIX koro: <http://w3id.org/koro#> 
SELECT ?object ?current ?target
WHERE {
    ?object koro:hasCurrentLocation ?current ;
    koro:hasTargetLocation ?target .
    FILTER (?current = ?target)
}"""

results = g.query(query)
print("\nObjects with the same current and target locations:")
for row in results:
    print(f"Object: {row.object}")  

query = """PREFIX koro: <http://w3id.org/koro#>
SELECT ?object ?location
WHERE {
    ?object a koro:Object ;
    koro:hasTargetLocation ?location .
}
"""

results = g.query(query)
print("\nObjects with a target location:")
for row in results:
    print(f"Object: {row.object}, Target Location: {row.location}")


query = """PREFIX koro: <http://w3id.org/koro#>
SELECT (COUNT(?object) AS ?count)
WHERE {
  ?object koro:hasCurrentLocation koro:fridge .
}"""

results = g.query(query)
print("\nNumber of objects in the fridge:")
for row in results: 
    print(f"Count: {int(row['count'])}")

query = """PREFIX koro: <http://w3id.org/koro#>
SELECT (COUNT(?object) AS ?count)
WHERE {
  ?object koro:hasTargetLocation koro:fridge .
}"""

results = g.query(query)
print("\nNumber of objects belonging in the fridge:")
for row in results:
    print(f"Count: {int(row['count'])}")


query = """PREFIX koro: <http://w3id.org/koro#>
SELECT (COUNT(?object) AS ?count)
WHERE {
  ?object koro:hasTargetLocation koro:fridge .
  FILTER NOT EXISTS {
    ?object koro:hasCurrentLocation koro:fridge .
  }
}"""

results = g.query(query)
print("\nNumber of objects belonging in the fridge that are not currently in the fridge:")
for row in results:
    print(f"Count: {int(row['count'])}")