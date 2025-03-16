from dataclasses import dataclass, field
from typing import List, Dict
from ddf_ra_tools.model.descriptor import Descriptor
from ddf_ra_tools.model.uml_class_property import UMLClassProperty


@dataclass
class UMLClass(Descriptor):
    isAbstract: bool = None
    properties: Dict[str, UMLClassProperty] = field(default_factory=lambda: {})
    superClasses: List[str] = field(default_factory=lambda: [])
    subClasses: List[str] = field(default_factory=lambda: [])

    def __repr__(self):
        return super().__repr__()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


@dataclass
class UMLClassDict:
    source: str
    version: str
    classes: Dict[str, UMLClass] = field(default_factory=lambda: {})
