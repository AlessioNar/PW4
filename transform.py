from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import pandas as pd

def initialize_graph():
    g = Graph()
    base_uri = "http://benettondata.it/graph/"
    

    # Create namespace for the supplier network
    benetton = Namespace(base_uri)


    namespaces = {
        'ben': base_uri,
        'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
        'schema': "http://schema.org/",
        'gr': "http://purl.org/goodrelations/v1#",        
        'foaf': "http://xmlns.com/foaf/0.1/",        
    }
    for prefix, uri in namespaces.items():
        g.bind(prefix, Namespace(uri), override=True)
    

    return g, base_uri, benetton


def initialize_classes(g, base_uri, csv_data, namespace):
    
    benetton = namespace

    g.add((benetton['ProductType'], RDF.type, RDFS.Class))
    g.add((benetton['ProductType'], RDFS.label, Literal("Represents types of products in the Benetton supply chain.")))
    
    g.add((benetton['Certificate'], RDF.type, RDFS.Class))
    g.add((benetton['Certificate'], RDFS.label, Literal("Represents certifications that a supplier might have.")))

    g.add((benetton['UnionInfo'], RDF.type, RDFS.Class))
    g.add((benetton['UnionInfo'], RDFS.label, Literal("Contains information about trade unions associated with the supplier.")))

    g.add((benetton['ProcessType'], RDF.type, RDFS.Class))
    g.add((benetton['ProcessType'], RDFS.label, Literal("ProcessType class, part of the Benetton Suppliers Ontology and that represents the various processes that are carried out by the supplier's network")))


    process_type_mapping = {
        'MANUFACTURING': 'Manufacturing',
        'OTHER_PROCESSING': 'OtherProcessing',
        'PRINTING': 'Printing',
        'SPINNING': 'Spinning',
        'WEAVING': 'Weaving',
        'WET_PROCESS': 'WetProcess'
    }

    # Instantiate the ProcessType class    
    for label, className in process_type_mapping.items():                
        process_uri = URIRef(base_uri + className)
        g.add((process_uri, RDF.type, benetton['ProcessType']))
        #g.add((process_uri, RDF.type, URIRef("gr:BusinessFunction")))
        g.add((process_uri, RDFS.label, Literal(className)))


    product_type_mapping = {
        'APPAREL': 'Apparel',
        'SHOES': 'Shoes',
        'ACCESSORIES': 'Accessories'
    }

    # Instantiate the ProductType class    
    for label, className in product_type_mapping.items():    
        product_uri = URIRef(base_uri+className)
        g.add((product_uri, RDF.type, benetton['ProductType']))
        #g.add((product_uri, RDF.type, URIRef("gr:ProductOrService")))
        g.add((product_uri, RDFS.label, Literal(className)))
    
    unique_certifications = set()

    for index, row in csv_data.iterrows():
        if row['hasCertifications']:
            cert_groups = row['CERTIFICATIONS'].split(';')
            for group in cert_groups:
                unique_certifications.update(cert.strip() for cert in group.split(','))
    
    unique_certifications.discard('')
    sanitized_certifications = {cert.replace(' ', '').replace('.', '').replace(',', '') for cert in unique_certifications}

    for cert in sanitized_certifications:
        cert_uri = URIRef(f"{base_uri}{cert}")
        g.add((cert_uri, RDF.type, benetton['Certificate']))
        g.add((cert_uri, RDFS.label, Literal(cert)))

def initialize_properties(g, base_uri, namespace):
    benetton = namespace
    
    def add_property(prop_name, label):
        prop_uri = URIRef(base_uri + prop_name)
        g.add((prop_uri, RDF.type, RDF.Property))
        g.add((prop_uri, RDFS.label, Literal(label)))

    add_property("hasProcess", "Indicates the processes a company is involved in.")
    add_property("hasProductType", "Indicates the types of products a company produces.")
    add_property("hasCertificate", "Indicates the certificates a company holds.")
    add_property("minEmployees", "Indicates the minimum number of employees in the company.")
    add_property("maxEmployees", "Indicates the maximum number of employees in the company.")
    add_property("percentageOfMen", "Indicates the percentage of men in a company.")
    add_property("percentageOfWomen", "Indicates the percentage of women in a company.")
    add_property("percentageOfMigrants", "Indicates the percentage of migrant workers in a company.")
    add_property("hasWorkersRepresentative", "Indicates if an organization has workers' representatives.")
    add_property("hasTradeUnion", "Indicates if a company has a trade union.")
    add_property("tradeUnionName", "Name of the trade union within the company.")
    add_property("collectiveBargainingAgreement", "Indicates if a company has a collective bargaining agreement.")
    add_property("coverageCBA", "Percentage of workforce covered by the collective bargaining agreement.")

def add_companies(g, base_uri, csv_data, namespace):
    
    # Define the schema namespace
    schema = Namespace("http://schema.org/")
    gr = Namespace("http://purl.org/goodrelations/v1#")

    # Bind the schema namespace to the "schema" prefix in the graph
    g.bind("schema", schema)
    g.bind("gr", gr)

    def add_literal(subject, predicate, obj, datatype=None):
        g.add((subject, URIRef(base_uri + predicate), Literal(obj, datatype=datatype)))

    for index, row in csv_data.iterrows():
        unique_id = f"C{index}"
        subject_uri = URIRef(base_uri + unique_id)
        address_uri = URIRef(base_uri + unique_id + "/address")

        g.add((subject_uri, RDF.type, gr.BusinessEntity))
        add_literal(subject_uri, 'name', row['COMPANY NAME'])

        g.add((address_uri, RDF.type, schema.PostalAddress))
        g.add((address_uri, schema.addressCountry, Literal(row['COUNTRY'])))
        g.add((address_uri, schema.addressRegion, Literal(row['COUNTY'])))
        g.add((address_uri, schema.postalCode, Literal(row['ZIP'])))
        g.add((address_uri, schema.addressLocality, Literal(row['CITY'])))
        g.add((address_uri, schema.streetAddress, Literal(row['STREET'])))

        process_type_mapping = {
        'MANUFACTURING': 'Manufacturing',
        'OTHER_PROCESSING': 'OtherProcessing',
        'PRINTING': 'Printing',
        'SPINNING': 'Spinning',
        'WEAVING': 'Weaving',
        'WET_PROCESS': 'WetProcess'
        }
        
        product_type_mapping = {
        'APPAREL': 'Apparel',
        'SHOES': 'Shoes',
        'ACCESSORIES': 'Accessories'
        }

        for col, rdf_type in process_type_mapping.items():
            if row[col]:
                add_literal(subject_uri, 'hasProcess',  URIRef(base_uri + rdf_type))
                            
        for col, rdf_type in product_type_mapping.items():
            if row[col]:
                add_literal(subject_uri, 'hasProductType', URIRef(base_uri + rdf_type))

        if row['hasCertifications']:
            for cert in row['CERTIFICATIONS'].split(';'):
                sanitized_cert = cert.strip().replace(' ', '_').replace('.', '').replace(',', '')
                add_literal(subject_uri, 'hasCertificate', URIRef(base_uri + sanitized_cert ))

        if row["MIN_EMPLOYEES"]:
            add_literal(subject_uri, 'minEmployees', row["MIN_EMPLOYEES"], XSD.numeric)
            add_literal(subject_uri, 'maxEmployees', row["MAX_EMPLOYEES"], XSD.numeric)

        if row["% MEN"]:
            add_literal(subject_uri, 'percentageOfMen', row["% MEN"], XSD.decimal)
            add_literal(subject_uri, 'percentageOfWomen', row["% WOMEN"], XSD.decimal)

        if row["% MIGRANT WORKERS"]:
            add_literal(subject_uri, 'percentageOfMigrants', row["% MIGRANT WORKERS"], XSD.decimal)

        if row["WORKERS' REPRESENTATIVES"]:
            add_literal(subject_uri, 'hasWorkersRepresentative', row["WORKERS' REPRESENTATIVES"])

        if row['TRADE UNION']:
            add_literal(subject_uri, 'hasTradeUnion', row['TRADE UNION'])
            add_literal(subject_uri, 'tradeUnionName', row['NAME OF THE TRADE UNION'])

        if row['COLLECTIVE BARGAINING AGREEMENT']:
            add_literal(subject_uri, 'collectiveBargainingAgreement', row['COLLECTIVE BARGAINING AGREEMENT'])
            add_literal(subject_uri, 'coverageCBA', row['% WORKFORCE COVERED BY THE CBA'], XSD.decimal)



def main(csv_path, output_path):
    csv_data = pd.read_csv(csv_path)
    g, base_uri, namespace = initialize_graph()
    initialize_classes(g, base_uri, csv_data, namespace)
    
    initialize_properties(g, base_uri, namespace)

    add_companies(g, base_uri, csv_data, namespace)

    turtle_data = g.serialize(format='turtle')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(turtle_data)

# Example usage
main('data/BenettonData.csv', 'data/benettonsuppliers.ttl')
