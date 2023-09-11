from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery
import pandas as pd

# Define RDF namespaces and prefixes
namespaces = {
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
    'schema1': "http://schema.org/",
    'gr': "http://purl.org/goodrelations/v1#",
    'foaf': "http://xmlns.com/foaf/0.1/",
    'ben': "http://benettondata.it/graph/"
}

# Define RDF graph
g = Graph()
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)
g.bind('schema1', Namespace(namespaces['schema1']))
g.bind('gr', Namespace(namespaces['gr']))
g.bind('foaf', Namespace(namespaces['foaf']))
g.bind('ben', Namespace(namespaces['ben']))

# Load RDF data from turtle file
g.parse('data/benettonsuppliers.ttl', format='turtle')
# Define query descriptions
query_descriptions = {
    'query1': "Count Companies with Wet Process and Certificates",
    'query2': "In how many countries does the Benetton Group supply from?",
    'query3': "Calculate Averages of Men, Women, and Migrant Percentages by Country",
    'query4': "List Company Names with Collective Bargaining Agreements (CBA) and Coverage Percentages"
}

# Prepare SPARQL queries
queries = {
    'query1': prepareQuery("""
    
   SELECT (COUNT(?company) AS ?count) WHERE {
    ?company a gr:BusinessEntity.
    ?company ben:hasProcess ben:Manufacturing.
    ?company ben:hasCertificate ?certificate.
    FILTER(?certificate != "")
}
    """, initNs=namespaces),

    'query2': prepareQuery("""
       SELECT (COUNT(DISTINCT ?country) AS ?count)
        WHERE {
        ?company a gr:BusinessEntity.
        ?company ben:hasProcess ben:WetProcess.
        ?company ben:hasCertificate ?cert.
        ?company ben:hasProductType ben:Apparel.
        ?company ?addressProp ?address.
        ?address schema1:addressCountry ?country.
        FILTER(?addressProp = schema1:address)
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

# Execute and print query descriptions and results
for query_name, query in queries.items():
    print(f"{query_descriptions[query_name]}")    

    results = g.query(query)
    for row in results:
        print(row)
    print()