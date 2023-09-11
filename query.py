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
g.bind('ben', Namespace(namespaces['ben']))

# Load RDF data from turtle file
g.parse('data/benettonsuppliers.ttl', format='turtle')
# Define query descriptions
query_descriptions = {
    'query1': "What is the percentage of companies that perform wet process manufacturing have a certificates?",
    'query2': "What percentage of employees are on average covered by CBAs for companies which perform wet processes manifacturing, produce apparel, hold certificates and have collective bargaining agreements (CBA)?",    
    'query3':"Retrieve a list of companies and their names where each company is classified as a 'BusinessEntity,' has a name, is engaged in 'Manufacturing' processes, produces 'Shoes,' and has a percentage of women employees greater than 70%",
}

# Prepare SPARQL queries
queries = {
    'query1': prepareQuery("""
  SELECT
  ((COUNT(?companyWithWetProcessAndCert) / ?totalCompaniesWithWetProcess) * 100.0 AS ?percentage)
WHERE {
  {
    SELECT (COUNT(?company) AS ?totalCompaniesWithWetProcess)
    WHERE {
      ?company a gr:BusinessEntity.
      ?company ben:hasProcess ben:WetProcess.
    }
  }
  {
    SELECT (COUNT(?company) AS ?companyWithWetProcessAndCert)
    WHERE {
      ?company a gr:BusinessEntity.
      ?company ben:hasProcess ben:WetProcess.
      ?company ben:hasCertificate ?certificate.
      FILTER(?certificate != "")
    }
  }
}
    """, initNs=namespaces),

    'query2': prepareQuery("""
       SELECT (AVG(?cbaPercentage) AS ?avgCBA)
WHERE {
  ?company a gr:BusinessEntity.
  ?company ben:hasProcess ben:WetProcess.
  ?company ben:hasProductType ben:Apparel.
  ?company ben:hasCertificate ?certificate.
  ?company ben:collectiveBargainingAgreement true.
  ?company ben:coverageCBA ?cbaPercentage.
}

    """, initNs=namespaces),

'query3':"""
SELECT ?company ?name
WHERE {
  ?company a gr:BusinessEntity.
  ?company ben:name ?name.
  ?company ben:hasProcess ben:Manufacturing.
  ?company ben:hasProductType ben:Shoes.
  ?company ben:percentageOfWomen ?percentage.
  FILTER (isLiteral(?percentage) && xsd:decimal(?percentage) > 70)
}


"""

}

# Execute and print query descriptions and results
for query_name, query in queries.items():
    print(f"{query_descriptions[query_name]}")    
    print()
    results = g.query(query)
    for row in results:
        formatted_row = [f"{str(value.n3())}" for value in row]
        print(" | ".join(formatted_row))
    print()