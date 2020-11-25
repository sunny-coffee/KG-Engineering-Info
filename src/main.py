from text_extractor import TextExtractor
from table_extractor import TableExtractor
from ontology_creator import OntologyCreator

IRI = "http://example.org/logistics-onto.owl"
FILE = "logistics-onto.owl"
filename = '161241_Flachzylinder_DZF.pdf' 

tableExtractor1 = TableExtractor(filename)
list1 = tableExtractor1.getTable()
print(list1)
ontologyCreator1 = OntologyCreator(IRI,FILE)
textExtractor1 = TextExtractor(filename)
category1 = textExtractor1.getCategory()


for i in range(len(list1)):
    ontologyCreator1.dynamically_add_classes(category1[0], list1[i])
    for j in range(28):
        ontologyCreator1.dynamically_add_instances(category1[1], category1[0], list1[i])

# from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
#      InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty, types

# IRI = "http://example.org/logistics-onto.owl"
# FILE = "logistics-onto.owl"

# onto = get_ontology(FILE).load()
# with onto:
    
#     class ddddd(Thing):
#         comment = ['i']
#     new_class = types.new_class('kkkkkkk',(DatatypeProperty,))

#     product_class = types.new_class('className',(getattr(onto,'role'),))
# onto.save(FILE)
