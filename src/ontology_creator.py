from owlready2 import DataProperty, FunctionalProperty, get_ontology, ObjectProperty, Thing, types
from owlready2.prop import DataPropertyClass, ObjectPropertyClass, ThingClass
import pandas as pd
import re

class OntologyCreator:
    __filename: str

    def __init__(self, iri,filename):
        self.__filename = filename
        onto = get_ontology(iri)
        onto.save(file=filename)

    #create a new class 
    def create_class(self, onto, className, classType):
        if className[0].isupper() and className[1].islower():
            className = self.processStr(className[:1].lower() + className[1:])
        else:
            className = self.processStr(className)
        obj = getattr(onto,className.replace(" ", "_"))
        if classType =='Thing':
            if obj != None:
                if type(obj) == ThingClass:
                    newClass = obj
                else:
                    newClass = types.new_class(className+'/Thing',(Thing,))
            else:
                newClass = types.new_class(className,(Thing,))
        elif classType =='ObjectProperty':
            if obj != None:
                if type(obj) == ObjectPropertyClass:
                    newClass = obj
                else:
                    newClass = types.new_class(className+'/ObjectProp',(ObjectProperty,))
            else:
                newClass = types.new_class(className,(ObjectProperty,))
        elif classType =='DataProperty':
            if obj != None:
                if type(obj) == DataPropertyClass:
                    newClass = obj
                else:
                    newClass = types.new_class(className+'/Dataprop',(DataProperty,))
            else:
                newClass = types.new_class(className,(DataProperty,))
        return newClass

    def dynamically_add_restrictions(self, input_df):
        """create restriction from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            for index, row in input_df.iterrows():
                superclass = self.create_class(onto, row['superclass'], "Thing")
                subclass = self.create_class(onto, row['subclass'], "Thing")
                subclass.is_a.append(superclass)
                if Thing in subclass.is_a:
                    subclass.is_a.remove(Thing)
                    
                for rel in row['relation']:
                    pobj = self.create_class(onto, rel[1], "Thing")
                    predicate = self.create_class(onto, rel[0], "ObjectProperty")
                    subclass.is_a.append(predicate.some(pobj))
        onto.save(file = self.__filename)


    def dynamically_add_relations(self, input_df):
        """create classes from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            for index, row in input_df.iterrows():
                new_object = self.create_class(onto, row['object'], "Thing")
                new_subject = self.create_class(onto, row['subject'], "Thing")
                relation = self.create_class(onto, row['relation'], "ObjectProperty")
                new_subject.is_a.append(relation.some(new_object))
        onto.save(file = self.__filename)

    def dynamically_add_category(self, input_df):
        """create classes from list"""
        onto = get_ontology(self.__filename).load()
        with onto:
            for index, row in input_df.iterrows():
                superclass = self.create_class(onto, row['superclass'], "Thing")
                subclass = self.create_class(onto, row['subclass'], "Thing")
                subclass.is_a.append(superclass)

                if Thing in subclass.is_a:
                    subclass.is_a.remove(Thing)

        onto.save(file = self.__filename)
    
    def add_from_referenceList(self, referenceList):
        supList = []
        onto = get_ontology(self.__filename).load()
        with onto:
            class hasProperty(ObjectProperty):
                pass
            class hasValue(DataProperty):
                pass
            class hasUnit(DataProperty):
                pass
            for tdf in referenceList:
                attrList = tdf.columns
                if ('Product type' in attrList or 'Type' in attrList) and ('Order no.' in attrList or 'no.' in attrList):
                    prodType = None
                    prodNum = None
                    propList = []
                    for prop in attrList:
                        # print(prop)
                        if prop == 'Product type' or prop == 'Type':
                            prodType = prop
                        elif prop == 'Order no.' or prop == 'no.':
                            prodNum = prop
                        else:      
                            propList.append(prop)
                    if prodType == None or prodNum == None:
                        continue

                    for index, row in tdf.iterrows():
                       
                        supClass = self.create_class(onto, row[prodType], 'Thing')
                        supList.append(supClass)
                        subClass = self.create_class(onto, row[prodNum].replace(' ',''), 'Thing')
                        subClass.is_a.append(supClass)

                        if Thing in subClass.is_a:
                            subClass.is_a.remove(Thing)

                        for prop in propList:
                            supprop = self.create_class(onto,prop, 'Thing')
                            subprop = self.create_class(onto,prop+'_'+row[prodNum].replace(' ',''), 'Thing')
                            subprop.is_a.append(supprop)

                            if Thing in subprop.is_a:
                                subprop.is_a.remove(Thing)
                            
                            subClass.is_a.append(hasProperty.only(subprop))
                            # print(row[prop])
                            subprop.is_a.append(hasValue.value(row[prop])) 
        onto.save(file = self.__filename)
        return supList

    def add_from_otherList(self, otherList, supList):
        onto = get_ontology(self.__filename).load()
        with onto:
            class hasProperty(ObjectProperty):
                pass
            class hasValue(DataProperty):
                pass
            class hasUnit(DataProperty):
                pass
            for tdf in otherList:

                if tdf.shape[1] == 2:
                    prop = tdf.columns[0]
                    val = tdf.columns[1]
                    propCategory = self.create_class(onto, prop, 'Thing')
                    for index, row in tdf.iterrows():
                        supprop = self.create_class(onto, row[prop], 'Thing')
                        supprop.is_a.append(propCategory)
                        if Thing in supprop.is_a: 
                            supprop.is_a.remove(Thing)
                        for supClass in supList:
                            subprop = self.create_class(onto, row[prop]+'_'+supClass.__name__, 'Thing')
                            subprop.is_a.append(supprop)
                            if Thing in subprop.is_a:
                                subprop.is_a.remove(Thing)
                            subprop.is_a.append(hasValue.value(row[val])) 
                            supClass.is_a.append(hasProperty.only(subprop))

                if tdf.shape[1] > 2:
                    attrList = tdf.columns
                    prop = None
                    prodNum = []
                    for index, attr in enumerate(attrList):
                        if index == 0:
                            prop = attr
                        else:
                            prodNum.append(attr.replace(' ',''))

                    propCategory = self.create_class(onto, prop, 'Thing')
                    for index, row in tdf.iterrows():
                        supprop = self.create_class(onto, row[prop], 'Thing')
                        supprop.is_a.append(propCategory)
                        if Thing in supprop.is_a: 
                            supprop.is_a.remove(Thing)

                        for num in prodNum:
                            subClass = self.create_class(onto, num, 'Thing')
                            subprop = self.create_class(onto, row[prop]+'_'+num, 'Thing')
                            subprop.is_a.append(supprop)
                            if Thing in subprop.is_a:
                                subprop.is_a.remove(Thing)
                            subprop.is_a.append(hasValue.value(row[num])) 
                            subClass.is_a.append(hasProperty.only(subprop))

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


    