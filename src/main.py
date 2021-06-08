from text_extractor import TextExtractor
# from triples_extractor_dp import DP2TriplesExtractor
from triples_extractor_srl  import TriplesExtractor
from table_extractor import TableExtractor
from ontology_creator import OntologyCreator
import os


# create an ontology

IRI = "http://example.org/engineering-info.owl"
FILE = "ontology.owl"
ontologyCreator1 = OntologyCreator(IRI,FILE)



# extract triples from a manual and organize these triples into the created ontology

filename = "../data/en/manual/PSSuniversal_Inst_Manual_21262-EN-07.pdf"
textExtractor1 = TextExtractor(filename)
text = textExtractor1.getText()
triplesExtractor1 = TriplesExtractor(text)
triples = triplesExtractor1.getTriples()
print(triples[1])
ontologyCreator1.text2Onto(triples)



# # extract property-value pairs from a table of Type 2 or Type 3 and organize these pairs into the created ontology

# filename = "../data/en/data_sheet/Pilz/S1MN_Data_sheet_1003088-EN-01.pdf"
# tableExtactor1 = TableExtractor(filename)
# otherList , referenceList = tableExtactor1.getTable()
# ontologyCreator1 = OntologyCreator(IRI,FILE)
# supList = ontologyCreator1.add_from_referenceList(referenceList)
# ontologyCreator1.add_from_otherList(otherList, supList)



## extract triples from several manual

# path = "../data/en/manual"
# files= os.listdir(path) 
# for file in files:
#     if not os.path.isdir(file): 
#         filename = path+"/"+file
#         print(filename)
#         textExtractor1 = TextExtractor(filename)
        # textExtractor1 = TextExtractor(filename)
        # text = textExtractor1.getText()
        # triplesExtractor1 = TriplesExtractor(text)
        # triples = triplesExtractor1.getTriples()
        # ontologyCreator1.text2Onto(triples)




