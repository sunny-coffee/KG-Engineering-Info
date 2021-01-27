from owlready2 import DatatypeProperty, FunctionalProperty, get_ontology, Inverse, \
     InverseFunctionalProperty, ObjectProperty, Thing, TransitiveProperty, SymmetricProperty,types
import pandas as pd
import re

class OntologyCreator:
    # __iri: str
    __filename: str

    def __init__(self, iri,filename):
        # self.__iri = iri
        self.__filename = filename
        onto = get_ontology(iri)
        onto.save(file=filename)

    def dynamically_add_restrictions(self, input_df):
        """create restriction from list"""
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
                    sup_predicate.domain.append(subclass)
                    sup_predicate.range.append(pobj)
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
                sup_relation.domain.append(new_subject)
                sup_relation.range.append(new_object)
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
    
    def add_from_referenceList(self, referenceList):
        instances = []
        onto = get_ontology(self.__filename).load()
        with onto:
            # classes
            class product_Pilz(Thing):
                comment = ["parent class of all Pilz products"]
            class P2HZ_X1(product_Pilz):
                pass
            # class hasAttributeOf(ObjectProperty):
            #     domain = [P2HZ_X1]
            attrSuperClass = types.new_class('Order_reference',(Thing,))
            for tdf in referenceList:
                    attrList = tdf.columns
                    # print(attrList)
                    if ('Product type' in attrList or 'Type' in attrList) and 'Order no.' in attrList:
                        # print('11111')
                        # print(tdf)

                        for index, row in tdf.iterrows():
                            product_instance = P2HZ_X1(self.processStr(row['Order no.'].replace(' ','')))
                            instances.append(product_instance)
                            for attr in attrList:
                                if len(attr):
                                    if len(row[attr]):
                                        attrspan = self.processStr(attr)
                                        attrClass = types.new_class(attrspan,(attrSuperClass,))
                                        value = types.new_class('value',(DatatypeProperty, FunctionalProperty,))
                                        value.domain.append(attrClass)
                                        value.range.append(str)
                                        relation = types.new_class('hasAttribute',(ObjectProperty,FunctionalProperty,))
                                        relation.domain.append(P2HZ_X1)
                                        relation.range.append(attrClass)
                                        attr_instance = attrClass()
                                        setattr(attr_instance, 'value', row[attr])
                                        setattr(product_instance, 'hasAttributeOf', attr_instance)
        onto.save(file = self.__filename)
        return instances
        #     for tdf in referenceList:
        #         attrList = tdf.columns
        #         # print(attrList)
        #         if ('Product type' in attrList or 'Type' in attrList) and 'Order no.' in attrList:
        #             # print('11111')
        #             # print(tdf)
        #             for attr in attrList:
        #                 if len(attr):                   
        #                     attrspan = self.processStr(attr)
        #                     attrSuperClass = types.new_class(attrspan,(Thing,))
        #                     attrClass = types.new_class(attrspan+'_of_S1EN',(attrSuperClass,))
        #                     value = types.new_class('valueOf'+attrspan,(DatatypeProperty, FunctionalProperty,))
        #                     value.domain.append(attrClass)
        #                     value.range.append(str)
        #                     relation = types.new_class('hasAttributeOf'+attrspan,(hasAttributeOf,))
        #                     relation.domain.append(P2HZ_X1)
        #                     relation.range.append(attrClass)
        #             for index, row in tdf.iterrows():
        #                 product_instance = P2HZ_X1(self.processStr(row['Order no.'].replace(' ','')))
        #                 instances.append(product_instance)
        #                 for attr in attrList:
        #                     if len(attr):
        #                         if len(row[attr]):
        #                             attrspan = self.processStr(attr)
        #                             attr_instance = getattr(onto, attrspan+'_of_S1EN')()
        #                             # print(type(getattr(attr_instance, 'valueOf'+attrspan)))
        #                             # print(type(row[attr]))
        #                             setattr(attr_instance, 'valueOf'+attrspan, row[attr])
        #                             getattr(product_instance, 'hasAttributeOf'+attrspan).append(attr_instance)
        # onto.save(file = self.__filename)
        # return instances

    def add_from_otherList(self, otherList, instances):
        onto = get_ontology(self.__filename).load()
        with onto:
            class product_Pilz(Thing):
                comment = ["parent class of all Pilz products"]
            class P2HZ_X1(product_Pilz):
                pass
            # class hasAttributeOf(ObjectProperty):
            #     domain = [P2HZ_X1]

            for tdf in otherList:
                if tdf.shape[1] == 2:
                    list0 = tdf.columns
                    attr = list0[0]
                    val = list0[1]
                    if type(val) == int:
                        product_instance = P2HZ_X1(self.processStr(val.replace(' ','')))
                        iterinstances = [product_instance]
                    else:
                        iterinstances = instances

                    attrSuperClass = types.new_class(self.processStr(attr),(Thing,))
                    for index, row in tdf.iterrows():
                        attrspan = self.processStr(row[attr])
                        # print(attrspan)
                        attrClass = types.new_class(attrspan,(attrSuperClass,))
                        # value = types.new_class('valueOf'+attrspan,(DatatypeProperty, FunctionalProperty,))
                        value = types.new_class('value',(DatatypeProperty, FunctionalProperty,))
                        value.domain.append(attrClass)
                        value.range.append(str)
                        # relation = types.new_class('hasAttribute'+attrspan,(hasAttributeOf,))
                        # relation.domain.append(P2HZ_X1)
                        # relation.range.append(attrClass)
                        relation = types.new_class('hasAttribute',(ObjectProperty,FunctionalProperty,))
                        relation.domain.append(P2HZ_X1)
                        relation.range.append(attrClass)
                        attr_instance = attrClass()
                        # print(row[val])
                        # setattr(attr_instance, 'valueOf'+attrspan, row[val])
                        setattr(attr_instance, 'value', row[val])
                        for instance in iterinstances:
                            # getattr(instance, 'hasAttributeOf'+attrspan).append(attr_instance)
                            setattr(instance, 'hasAttribute', attr_instance)
        onto.save(file = self.__filename)
        # return instances

    def processStr(self,str):
        str1 = re.sub(r"\s+|,|-|/|\(|\)|:|\||\n|\[|\]", ' ',str.replace("-\n", "").replace("- ", " "))
        str2 = str1.replace('°C',' degree').replace(' x ','x').replace('  ',' ').replace('=','equal').strip()
        str3 = str2.replace(' ','_')
        return str3

    def text2Onto(self,triplesList):
        if not triplesList[0].empty:
            self.dynamically_add_restrictions(triplesList[0])
        if not triplesList[1].empty:
            self.dynamically_add_relations(triplesList[1])
        if not triplesList[2].empty:
            self.dynamically_add_category(triplesList[2])


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
     