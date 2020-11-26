from text_extractor import TextExtractor
from table_extractor import TableExtractor
from ontology_creator import OntologyCreator
import os

IRI = "http://example.org/engineering-info.owl"
FILE = "engineering-info.owl"

ontologyCreator1 = OntologyCreator(IRI,FILE)



# filename = "../data/151160_Rückschlagventil_GRLA.pdf"

# tableExtractor1 = TableExtractor(filename)
# list1 = tableExtractor1.getTable()

# textExtractor1 = TextExtractor(filename)
# category1 = textExtractor1.getCategory()

# if len(list1):
#     pass
# else:
#     for i in range(len(list1)):
#         ontologyCreator1.dynamically_add_classes(category1[1], list1[i])
#         for j in range(28):
#             ontologyCreator1.dynamically_add_instances(category1[0], category1[1], list1[i])
   



path = "../data"
files= os.listdir(path) 

for file in files:
    if not os.path.isdir(file): 
        filename = path+"/"+file
        print(filename)
        
    tableExtractor1 = TableExtractor(filename)
    list1 = tableExtractor1.getTable()
    textExtractor1 = TextExtractor(filename)
    category1 = textExtractor1.getCategory()

    if len(list1):
        for i in range(len(list1)):
            ontologyCreator1.dynamically_add_classes(category1[1], list1[i])
            for j in range(28):
                ontologyCreator1.dynamically_add_instances(category1[0], category1[1], list1[i])
        
        
   
        

