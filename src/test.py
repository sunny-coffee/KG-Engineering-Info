from text_extractor import TextExtractor
from triples_extractor import TriplesExtractor

filename = "../data/en/PSSuniversal_Inst_Manual_21262-EN-07.pdf"

textExtractor1 = TextExtractor(filename)
text = textExtractor1.getText()
triplesExtractor1 = TriplesExtractor(text)
triplesExtractor1.getTriples()


