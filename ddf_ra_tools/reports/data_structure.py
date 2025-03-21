from dataclasses import dataclass, field
from typing import Optional, List, Dict
from ddf_ra_tools.model.model_class import ModelClassDict
from ddf_ra_tools.config import (
    API_ONLY_PROPERTIES,
    DATA_STRUCTURE_CLASS_KEY_MAP,
    DATA_STRUCTURE_PROPERTY_KEY_MAP,
)
import yaml


@dataclass
class DataStructureTypeRef:
    ref: str

    def mapped(self):
        return {"$ref": f"#/{self.ref}"}


@dataclass
class DataStructurePropertyRecord:
    types: List[DataStructureTypeRef] = field(default_factory=lambda: [])
    defNciCode: Optional[str] = None
    preferredTerm: Optional[str] = None
    definition: Optional[str] = None
    cardinality: Optional[str] = None
    relationshipType: Optional[str] = "Value"
    modelName: Optional[str] = None
    modelRepresentation: Optional[str] = None
    inheritedFrom: Optional[str] = None

    def mapped(self):
        return {
            DATA_STRUCTURE_PROPERTY_KEY_MAP.get(k, k): v
            for k, v in self.__dict__.items()
            if v
        }


@dataclass
class DataStructureClassRecord:
    defNciCode: Optional[str] = None
    preferredTerm: Optional[str] = None
    definition: Optional[str] = None
    modifier: str = None
    superClasses: List[DataStructureTypeRef] = field(
        default_factory=lambda: []
    )
    subClasses: List[DataStructureTypeRef] = field(default_factory=lambda: [])
    attributes: Dict[str, DataStructurePropertyRecord] = field(
        default_factory=lambda: {}
    )

    def mapped(self):
        return {
            DATA_STRUCTURE_CLASS_KEY_MAP.get(k, k): v
            for k, v in self.__dict__.items()
            if v
        }


@dataclass
class DataStructureReport(yaml.YAMLObject):
    report: Dict[str, DataStructureClassRecord] = field(
        default_factory=lambda: {}
    )

    def __init__(self, combDict: ModelClassDict):
        def get_type_ref(typestr: str) -> DataStructureTypeRef:
            return DataStructureTypeRef(
                ref=typestr if typestr in combDict.classes else typestr.lower()
            ).mapped()

        self.report = {
            clsName: DataStructureClassRecord(
                defNciCode=clsDef.ctClass.defNciCode
                if clsDef.ctClass
                else None,
                preferredTerm=clsDef.ctClass.preferredTerm
                if clsDef.ctClass
                else None,
                definition=clsDef.ctClass.definition
                if clsDef.ctClass
                else None,
                modifier=clsDef.modifier,
                superClasses=[
                    get_type_ref(sc) for sc in clsDef.umlClass.superClasses
                ]
                if clsDef.umlClass
                else None,
                subClasses=[
                    get_type_ref(sc) for sc in clsDef.umlClass.subClasses
                ]
                if clsDef.umlClass
                else None,
                attributes={
                    prpDef.apiProperty.obj_name: DataStructurePropertyRecord(
                        types=[get_type_ref(t) for t in prpDef.types],
                        defNciCode=prpDef.ctProperty.defNciCode
                        if prpDef.ctProperty
                        else None,
                        preferredTerm=prpDef.ctProperty.preferredTerm
                        if prpDef.ctProperty
                        else None,
                        definition=prpDef.ctProperty.definition
                        if prpDef.ctProperty
                        else None,
                        cardinality=prpDef.cardinality,
                        relationshipType=prpDef.relationshipType,
                        modelName=prpDef.modelName,
                        modelRepresentation=prpDef.modelRepresentation,
                        inheritedFrom=[
                            get_type_ref(prpDef.umlProperty.inheritedFrom)
                        ]
                        if prpDef.umlProperty
                        and prpDef.umlProperty.inheritedFrom
                        else None,
                    ).mapped()
                    for prpDef in clsDef.properties.values()
                    if prpDef.apiProperty is not None
                }
                if clsDef.umlClass is None or clsDef.umlClass.isAbstract is False
                else {
                    prpDef.apiProperty.obj_name: DataStructurePropertyRecord(
                        types=[get_type_ref(t) for t in prpDef.types],
                        defNciCode=prpDef.ctProperty.defNciCode
                        if prpDef.ctProperty
                        else None,
                        preferredTerm=prpDef.ctProperty.preferredTerm
                        if prpDef.ctProperty
                        else None,
                        definition=prpDef.ctProperty.definition
                        if prpDef.ctProperty
                        else None,
                        cardinality=prpDef.cardinality,
                        relationshipType=prpDef.relationshipType,
                        modelName=prpDef.modelName,
                        modelRepresentation=prpDef.modelRepresentation,
                    ).mapped()
                    for prpDef in combDict.classes[
                        clsDef.umlClass.subClasses[0]
                    ].properties.values()
                    if prpDef.obj_name not in API_ONLY_PROPERTIES
                    and prpDef.apiProperty is not None
                    and (
                        prpDef.umlProperty is None
                        or prpDef.umlProperty.inheritedFrom == clsName
                    )
                },
            ).mapped()
            for clsName, clsDef in combDict.classes.items()
        }

    def to_yaml(self, ymlFile: str):
        with open(ymlFile, "w", newline="") as f:
            yaml.dump(self.report, f, sort_keys=False)
