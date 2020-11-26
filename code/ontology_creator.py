from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty,types
import pandas as pd


class OntologyCreator:
    __iri: str
    __filename: str

    def __init__(self, iri,filename):
        self.__iri = iri
        self.__filename = filename
        onto = get_ontology(iri)
        with onto:
            # classes
            class Product(Thing):
                comment = ["parent class of all products"]
            class Merkmal(DatatypeProperty):
                domain = [Product]
        onto.save(file=filename)

    def dynamically_add_classes(self, className, input_df):
        """create classes from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            product_class = types.new_class(className,(getattr(onto,'Product'),))
            for i in range(int(input_df.shape[0])):
                new_class = types.new_class(input_df.iloc[i,0].replace(" ", "_").replace(",", ""),(getattr(onto,'Merkmal'),))
                new_class.domain.append(product_class)
        onto.save(file = self.__filename)

    def dynamically_add_instances(self, instanceName, className,input_df):
        """create instances from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            new_instance = getattr(onto, className)(instanceName)
            for i in range(int(input_df.shape[0])): 
                s = input_df.iloc[i,0].replace(" ", "_").replace(",", "")
                        
                getattr(new_instance,s).append(input_df.iloc[i,1])
              
        onto.save(file = self.__filename)
     