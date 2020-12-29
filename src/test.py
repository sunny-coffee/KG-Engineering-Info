from text_extractor import TextExtractor
from triples_extractor import TriplesExtractor
from ontology_creator import OntologyCreator
# filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"

# textExtractor1 = TextExtractor(filename)
# text = textExtractor1.getText()
# # print(text)
text ='''  Analogue inputs and outputs plus the inputs '''

# text = 'suppressions can lead to errors on the on/off tests and test pulses.'
triplesExtractor1 = TriplesExtractor(text)
# print(triplesExtractor1.getPassiveTriples())
passiveTriples = triplesExtractor1.getPassiveTriples()
# print(passiveTriples[2])

activeTriples = triplesExtractor1.getActiveTriples()
# print(activeTriples[2])

IRI = "http://example.org/engineering-info.owl"
FILE = "engineering-info.owl"

ontologyCreator1 = OntologyCreator(IRI,FILE)

if not passiveTriples[0].empty:
    ontologyCreator1.dynamically_add_restrictions(passiveTriples[0])
if not passiveTriples[1].empty:
    ontologyCreator1.dynamically_add_relations(passiveTriples[1])
if not passiveTriples[2].empty:
    ontologyCreator1.dynamically_add_category(passiveTriples[2])
print(passiveTriples[2])

if not activeTriples[0].empty:
    ontologyCreator1.dynamically_add_restrictions(activeTriples[0])
if not activeTriples[1].empty:
    ontologyCreator1.dynamically_add_relations(activeTriples[1])
if not activeTriples[2].empty:
    ontologyCreator1.dynamically_add_category(activeTriples[2])
print(activeTriples[2])

