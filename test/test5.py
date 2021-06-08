from owlready2 import *


onto = get_ontology("http://test.org/onto.owl")

with onto:
    class DrugForm(Thing):
        pass
    class DrugForm2(Thing):
        pass
    class ii(DataProperty):
        pass
    class iiii(ObjectProperty):
        pass

# tablet     = DrugForm()
# capsule    = DrugForm()
# injectable = DrugForm()
# pomade     = DrugForm()
print(DrugForm.__name__, type(DrugForm.__name__))

# DrugForm.is_a.append(ii.value('11'))
# print(type(DrugForm).__name__)
# print(type(DrugForm) == ThingClass)

# Assert that there is only four possible drug forms
# DrugForm.is_a.append(OneOf([tablet, capsule, injectable, pomade]))

# onto.save('KKKKK.owl')