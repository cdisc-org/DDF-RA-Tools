from typing import Union
from ddf_ra_tools.model.uml_class import UMLClassDict
from ddf_ra_tools.model.ct_class import CTClassDict


def get_card(cardinality=None, cardLow=None, cardHigh=None):
    if cardLow:
        return (
            "{}..{}".format(cardLow, cardHigh)
            if cardHigh and cardHigh != cardLow
            else cardLow
        )
    else:
        return cardinality


def add_sub_classes(class_dict: Union[UMLClassDict, CTClassDict]):
    for (subClass, superClasses) in [
        (k, v.superClasses)
        for k, v in class_dict.classes.items()
        if len(v.superClasses) > 0
    ]:
        for superClass in [class_dict.classes[s] for s in superClasses]:
            superClass.subClasses.append(subClass)


def format_value(value):
    return ", ".join(value) if type(value) in [set, list] else value
