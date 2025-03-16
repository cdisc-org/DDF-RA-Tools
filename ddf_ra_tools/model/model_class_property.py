from dataclasses import dataclass, field
from typing import Optional, Set
from ddf_ra_tools.model.descriptor import Descriptor
from ddf_ra_tools.model.uml_class_property import UMLClassProperty
from ddf_ra_tools.model.api_class_property import APIClassProperty
from ddf_ra_tools.model.ct_class_property import CTClassProperty


@dataclass
class ModelClassProperty(Descriptor):
    umlProperty: Optional[UMLClassProperty] = None
    apiProperty: Optional[APIClassProperty] = None
    ctProperty: Optional[CTClassProperty] = None
    modelRepresentation: Optional[str] = None
    types: Set[str] = field(default_factory=lambda: set())
    cardinality: Optional[str] = None
    relationshipType: Optional[str] = "Value"
    modelName: Optional[str] = None

    def __post_init__(self):
        umlProperty = self.umlProperty or UMLClassProperty(
            obj_name=self.obj_name
        )
        apiProperty = self.apiProperty or APIClassProperty(
            obj_name=self.obj_name
        )
        ctProperty = self.ctProperty or CTClassProperty(obj_name=self.obj_name)
        self.modelRepresentation = (
            umlProperty.modelRepresentation or ctProperty.modelRepresentation
        )
        self.types = umlProperty.types or apiProperty.types
        self.cardinality = umlProperty.cardinality or apiProperty.cardinality
        if self.umlProperty:
            self.modelName = umlProperty.obj_name

    def __repr__(self):
        return super().__repr__()
