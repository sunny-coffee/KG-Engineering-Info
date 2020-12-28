from text_extractor import TextExtractor
from triples_extractor import TriplesExtractor
from ontology_creator import OntologyCreator
# filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"

# textExtractor1 = TextExtractor(filename)
# text = textExtractor1.getText()
# # print(text)
text ='''  Analogue inputs and outputs plus the inputs and outputs on the counter modules should always be connected using shielded cables.   The module connects the shield to the functional earth via the C-rail. Suppression should not be used to protect the digital semiconductor outputs. Digital semiconductor outputs on the PSSuniversal do not need suppression. 
With FS outputs on the PSSuniversal, suppressions can lead to errors on the on/off tests and test pulses. However, inductive loads that are not switched by the PSSuniversal should be wired with suppression elements for EMC reasons. Care must be taken to avoid interference when installing the unit within an enclosure or wall-mounting.   Earth bars, earth conductors and the housing should be attached to metal parts in order to divert any coupled interference on to large metal areas. For wall-mounting we recommend. that the overall potential surfaces are made of steel.  For varnished or anodised metal parts you should use special contact plates or remove the protective coating. an earth bar for the cable shields can also be 
used as the ground conductor bar.   If an earth bar for the cable shields is to be used as the earth conductor, comply with the latest regulations for earthing an earth bar for the cable shields. '''

# text = 'suppressions can lead to errors on the on/off tests and test pulses.'
triplesExtractor1 = TriplesExtractor(text)
# print(triplesExtractor1.getPassiveTriples())
passiveTriples = triplesExtractor1.getPassiveTriples()
print(passiveTriples)

activeTriples = triplesExtractor1.getActiveTriples()
print(activeTriples)

IRI = "http://example.org/engineering-info.owl"
FILE = "engineering-info.owl"

ontologyCreator1 = OntologyCreator(IRI,FILE)
if not passiveTriples.empty:
    ontologyCreator1.dynamically_add_classes(passiveTriples)

if not activeTriples.empty:
    ontologyCreator1.dynamically_add_classes(activeTriples)



