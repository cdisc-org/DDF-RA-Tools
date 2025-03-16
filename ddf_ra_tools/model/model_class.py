from dataclasses import dataclass, field
from typing import Optional, Dict
from ddf_ra_tools.model.descriptor import Descriptor
from ddf_ra_tools.model.model_class_property import ModelClassProperty
from ddf_ra_tools.model.uml_class import UMLClass, UMLClassDict
from ddf_ra_tools.model.api_class import APIClass, APIClassDict
from ddf_ra_tools.model.ct_class import CTClass, CTClassDict
from copy import deepcopy


@dataclass
class ModelClass(Descriptor):
    umlClass: Optional[UMLClass] = None
    apiClass: Optional[APIClass] = None
    ctClass: Optional[CTClass] = None
    modifier: str = None
    properties: Dict[str, ModelClassProperty] = field(
        default_factory=lambda: {}
    )

    def __post_init__(self):
        umlClass = self.umlClass or UMLClass(obj_name=self.obj_name)
        apiClass = self.apiClass or APIClass(obj_name=self.obj_name)
        ctClass = self.ctClass or CTClass(obj_name=self.obj_name)
        self.modifier = "Abstract" if umlClass.isAbstract else "Concrete"
        self.properties = {
            prop_name: ModelClassProperty(
                obj_name=prop_name,
                umlProperty=self.umlClass.properties.pop(prop_name)
                if prop_name in umlClass.properties
                else None,
                apiProperty=self.apiClass.properties.pop(prop_name)
                if prop_name in apiClass.properties
                else None,
                ctProperty=self.ctClass.properties.pop(prop_name)
                if prop_name in ctClass.properties
                else None,
            )
            for prop_name in (
                self.combined_keys(
                    d1=umlClass.properties,
                    d2=apiClass.properties,
                    d3=ctClass.properties,
                )
            )
        }

        for (idprop, idprpdef) in [
            (k, v)
            for k, v in self.properties.items()
            if v.apiProperty
            and (k.endswith("Id") or k.endswith("Ids"))
            and not (v.umlProperty or v.ctProperty)
        ]:
            valid_synonyms = idprpdef.apiProperty.synonyms & set(
                self.properties.keys()
            )
            if valid_synonyms:
                for synonym in valid_synonyms:
                    if self.properties[synonym].apiProperty:
                        print(
                            "There is already an API property for "
                            + f"{self.obj_name}.{synonym}"
                        )
                    else:
                        self.properties[synonym].apiProperty = idprpdef
                    self.properties[synonym].relationshipType = "Ref"
                self.properties.pop(idprop)

    def __repr__(self):
        return super().__repr__()

    def __hash__(self):
        return super().__hash__()

    def combined_keys(self, d1: dict, d2: dict, d3: dict) -> list:
        keylist = list(d1.keys())
        keylist.extend([k for k in d2.keys() if k not in keylist])
        keylist.extend([k for k in d3.keys() if k not in keylist])
        return keylist


@dataclass
class ModelClassDict:
    source: str
    version: str
    classes: Dict[str, ModelClass] = field(
        default_factory=Dict[str, ModelClass]
    )

    def __init__(
        self,
        umlDict: UMLClassDict = None,
        ctDict: CTClassDict = None,
        apiDict: APIClassDict = None,
    ):
        self.source = "All"
        self.version = (umlDict or ctDict or apiDict).version
        self.classes = {
            class_name: ModelClass(
                obj_name=class_name,
                umlClass=deepcopy(umlDict.classes.get(class_name, None)),
                ctClass=deepcopy(ctDict.classes.get(class_name, None)),
                apiClass=deepcopy(apiDict.classes.get(class_name, None)),
            )
            for class_name in (
                sorted(
                    umlDict.classes.keys()
                    | ctDict.classes.keys()
                    | apiDict.classes.keys()
                )
            )
        }
