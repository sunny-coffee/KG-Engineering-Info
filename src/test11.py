import spacy

nlp = spacy.load('en_core_web_lg')

doc1 = nlp('1 core flexible')
doc2 = nlp('Circuit breaker 24 VAC/DC, characteristic B/C')

doc1_doc2 = doc1.similarity(doc2)
print(doc1_doc2)

