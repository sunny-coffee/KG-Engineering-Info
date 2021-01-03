from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty,types
import pandas as pd


class OntologyCreator:
    # __iri: str
    __filename: str

    def __init__(self, iri,filename):
        # self.__iri = iri
        self.__filename = filename
        onto = get_ontology(iri)
        with onto:
            # classes
            class Product(Thing):
                comment = ["parent class of all products"]
            class Merkmal(DatatypeProperty):
                domain = [Product]
        onto.save(file=filename)

    def dynamically_add_restrictions(self, input_df):
        """create classes from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            for index, row in input_df.iterrows():

                sup = getattr(onto,row['superclass'].replace(" ", "_"))
                if sup != None:
                    superclass = sup
                else:
                    superclass = types.new_class(row['superclass'].replace(" ", "_"),(Thing,))

                subclass = types.new_class(row['subclass'].replace(" ", "_"),(superclass,))
                subclass.equivalent_to.append(superclass)
                for rel in row['relation']:
                    pobj = types.new_class(rel[1].replace(" ", "_"),(Thing,))
                    sup_predicate = types.new_class((rel[0]).replace(" ", "_"),(ObjectProperty,))
                    predicate = types.new_class((rel[0]+' '+rel[1]).replace(" ", "_"),(sup_predicate,))
                    predicate.domain.append(subclass)
                    predicate.range.append(pobj)
                    subclass.equivalent_to = [(predicate.some(pobj)) & subclass.equivalent_to[0]]
        onto.save(file = self.__filename)

    def dynamically_add_relations(self, input_df):
        """create classes from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            for index, row in input_df.iterrows():
                obj = getattr(onto,row['object'].replace(" ", "_"))
                if obj != None:
                    new_object = obj
                else:
                    new_object = types.new_class(row['object'].replace(" ", "_"),(Thing,))
                
                subj = getattr(onto,row['subject'].replace(" ", "_"))
                if subj != None:
                    new_subject = subj
                else:
                    new_subject = types.new_class(row['subject'].replace(" ", "_"),(Thing,))
                sup_relation = types.new_class(row['relation'].replace(" ", "_"),(ObjectProperty,))
                new_relation = types.new_class((row['relation']+ ' ' + row['object']).replace(" ", "_"),(sup_relation,))  
                new_relation.domain.append(new_subject)
                new_relation.range.append(new_object)
        onto.save(file = self.__filename)

    def dynamically_add_category(self, input_df):
        """create classes from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            for index, row in input_df.iterrows():
                superclass = types.new_class(row['superclass'].replace(" ", "_"),(Thing,))
                
                # sub = getattr(onto,row['subclass'].replace(" ", "_"))
                # print(type(superclass))
                # print(type(sub))
                # print(sub.is_a)
                subclass = types.new_class(row['subclass'].replace(" ", "_"),(superclass,))
                # if sub != None:
                #     subclass = sub
                # subclass.is_a.append(superclass)
                if Thing in subclass.is_a:
                    subclass.is_a.remove(Thing)
                # else:
                
                    
                # sup_relation = types.new_class(row['relation'].replace(" ", "_"),(ObjectProperty,))
                # new_relation = types.new_class((row['relation']+ ' ' + row['object']).replace(" ", "_"),(sup_relation,))  
                # new_relation.domain.append(new_subject)
                # new_relation.range.append(new_object)
        onto.save(file = self.__filename)


    # def dynamically_add_classes(self, className, input_df):
    #     """create classes from list"""
    #     onto = get_ontology(self.__filename).load()
    #     with onto:
    #         product_class = types.new_class(className,(getattr(onto,'Product'),))
    #         for i in range(int(input_df.shape[0])):
    #             new_class = types.new_class(input_df.iloc[i,0].replace(" ", "_").replace(",", ""),(getattr(onto,'Merkmal'),))
    #             new_class.domain.append(product_class)
    #     onto.save(file = self.__filename)

    # def dynamically_add_instances(self, instanceName, className,input_df):
    #     """create instances from list"""
    #     onto = get_ontology(self.__filename).load()
    #     with onto:
    #         new_instance = getattr(onto, className)(instanceName)
    #         for i in range(int(input_df.shape[0])): 
    #             s = input_df.iloc[i,0].replace(" ", "_").replace(",", "")
                        
    #             getattr(new_instance,s).append(input_df.iloc[i,1])
              
    #     onto.save(file = self.__filename)
     