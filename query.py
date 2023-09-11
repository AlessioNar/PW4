from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery
import pandas as pd

# Define RDF namespaces and prefixes
namespaces = {
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
    'schema': "http://schema.org/",
    'gr': "http://purl.org/goodrelations/v1#",
    'foaf': "http://xmlns.com/foaf/0.1/",
    'ben': "http://benettondata.it/graph"
}

# Define RDF graph
g = Graph()
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)
g.bind('schema', Namespace(namespaces['schema']))
g.bind('gr', Namespace(namespaces['gr']))
g.bind('foaf', Namespace(namespaces['foaf']))
g.bind('ben', Namespace(namespaces['ben']))

# Load RDF data from turtle file
g.parse('benettonsuppliers.ttl', format='turtle')

# Prepare SPARQL queries
queries = {
    'query1': prepareQuery("""
        SELECT (COUNT(?company) AS ?count) WHERE {
          ?company a gr:BusinessEntity.
          ?company ben:hasProcess ben:WetProcess.
          ?company ben:hasCertificate ?cert.
        }
    """, initNs=namespaces),
    'query2': prepareQuery("""
        SELECT ?companyName ?tradeUnionName WHERE {
          ?company a gr:BusinessEntity.
          ?company ben:hasTradeUnion true.
          ?company ben:tradeUnionName ?tradeUnionName.
          ?company ben:name ?companyName.
        }
    """, initNs=namespaces),
    'query3': prepareQuery("""
        SELECT ?country (AVG(?menPercentage) AS ?avgMen) (AVG(?womenPercentage) AS ?avgWomen) (AVG(?migrantPercentage) AS ?avgMigrants) WHERE {
          ?company a gr:BusinessEntity.
          ?company ben:address ?address.
          ?address schema:addressCountry ?country.
          ?company ben:percentageOfMen ?menPercentage.
          ?company ben:percentageOfWomen ?womenPercentage.
          ?company ben:percentageOfMigrants ?migrantPercentage.
        }
        GROUP BY ?country
    """, initNs=namespaces),
    'query4': prepareQuery("""
        SELECT ?companyName ?cbaPercentage WHERE {
          ?company a gr:BusinessEntity.
          ?company ben:collectiveBargainingAgreement true.
          ?company ben:coverageCBA ?cbaPercentage.
          ?company ben:name ?companyName.
        }
    """, initNs=namespaces),
}

# Execute and print query results
for query_name, query in queries.items():
    print(f"Query: {query_name}")
    results = g.query(query)
    for row in results:
        print(row)
    print()
