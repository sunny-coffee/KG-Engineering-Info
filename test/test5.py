from owlready2 import *

onto = get_ontology("http://test.org/onto.owl")

with onto:
    # class Drug(Thing):
    #     pass
    # class ActivePrinciple(Thing):
    #     pass
    # class has_for_active_principle(Drug >> ActivePrinciple):
    #     pass

    # class Placebo(Drug):
    #     equivalent_to = [Not(has_for_active_principle.some(ActivePrinciple))]

    class A(Thing):
        pass

    class B(Thing):
        pass

    class B(A):
        pass

onto.save('KKKKK.owl')