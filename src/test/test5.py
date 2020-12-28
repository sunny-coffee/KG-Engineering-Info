from owlready2 import *

onto = get_ontology("http://test.org/onto.owl")

with onto:
    class A(Thing):
        pass
    class B(Thing):
        pass

    class has_for_ingredient(ObjectProperty):
        domain    = [A]
        range     = [B]

    class C(Thing):
        pass

    class is_a(ObjectProperty):
        domain = [A]
        range = [C]

    class A(Thing):
        pass
#     class C(A):
#         equivalent_to = [A & has_for_ingredient.some(B)]

#     class has_ingredient(ObjectProperty):
#         domain    = [A]
#         range     = [B]
#     class has_special_relation(ObjectProperty):
#         domain    = [A]
#         range     = [has_for_ingredient]

# a = A()
# b = B()
# a.has_for_ingredient = [b]

# a.has_special_relation = a.has_ingredient
# kk = getattr(onto,'C')
# print(kk)

    Drug = types.new_class("Drug1", (Thing,))
onto.save('KKKKK')