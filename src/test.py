from text_extractor import TextExtractor
from triples_extractor_dp import DP2TriplesExtractor
from triples_extractor import TriplesExtractor
from ontology_creator import OntologyCreator
import os

# path = "../data/en/manual"
# files= os.listdir(path) 
# IRI = "http://example.org/engineering-info.owl"
# FILE = "engineering-info.owl"
# ontologyCreator1 = OntologyCreator(IRI,FILE)

# for file in files:
#     if not os.path.isdir(file): 
#         filename = path+"/"+file
#         print(filename)
#         textExtractor1 = TextExtractor(filename)
        # textExtractor1 = TextExtractor(filename)
        # text = textExtractor1.getText()
        # triplesExtractor1 = TriplesExtractor(text)
        # passiveTriples = triplesExtractor1.getPassiveTriples()
        # activeTriples = triplesExtractor1.getActiveTriples()
        # ontologyCreator1.text2Onto(passiveTriples)
        # ontologyCreator1.text2Onto(activeTriples)

filename = "../data/en/manual/PNOZ_e5_11p_Operat_Man_21364-EN-08.pdf"
textExtractor1 = TextExtractor(filename)
text = textExtractor1.getText()
# print(text)connect the shield to
# text ='''Digital inputs and outputs on the PSSu system do not need shielded cables. However, if the connection cables have a shield, it should be connected at one end. Analogue inputs and outputs plus the inputs and outputs on the counter modules should always be connected using shielded cables.'''
# text = '''At the end of the movement, the motion terminal closes the valve so that only the minimum static pressure sufficient to hold the cylinder in position is applied. '''
# text = "suppression can lead to errors on the on/off tests and test pulses."

# triplesExtractor = DP2TriplesExtractor(text) 
# triplesExtractor.getTriples()

triplesExtractor1 = TriplesExtractor(text)
passiveTriples = triplesExtractor1.getPassiveTriples()
activeTriples = triplesExtractor1.getActiveTriples()
# IRI = "http://example.org/engineering-info.owl"
# FILE = "test.owl"
# ontologyCreator1 = OntologyCreator(IRI,FILE)
# ontologyCreator1.text2Onto(passiveTriples)
# ontologyCreator1.text2Onto(activeTriples)
# print(activeTriples)

# print(triplesExtractor1.getPassiveTriples())
# passiveTriples = triplesExtractor1.getPassiveTriples()

print(passiveTriples[1])
print(activeTriples[1])

# activeTriples = triplesExtractor1.getActiveTriples()


