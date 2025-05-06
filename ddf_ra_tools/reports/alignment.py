from dataclasses import dataclass, field
from typing import Optional, List
from ddf_ra_tools.model.model_class import ModelClassDict
from ddf_ra_tools.model.model_class_property import ModelClassProperty
from ddf_ra_tools.utils import format_value
from ddf_ra_tools.config import (
    API_ONLY_CLASSES,
    API_ONLY_PROPERTIES,
    API_ONLY_CLASS_PROPERTIES,
    NON_CT_PROPERTIES,
    ALIGNMENT_COLUMN_MAP,
    VALID_API_UML_DATATYPES,
    ALIGNMENT_FILE_NAME,
)
import csv


@dataclass
class AlignmentRecord:
    cls: str
    attr: Optional[str] = None
    char: Optional[str] = None
    api: Optional[str] = None
    ct: Optional[str] = None
    uml: Optional[str] = None

    def __repr__(self):
        return str(
            {ALIGNMENT_COLUMN_MAP[k]: v for k, v in self.__dict__.items()}
        )


@dataclass
class AlignmentReport:
    records: List[AlignmentRecord] = field(default_factory=lambda: [])

    def __init__(self, combDict: ModelClassDict):
        self.records = []
        self.absCls = [
            k
            for k, v in combDict.classes.items()
            if v.umlClass and v.umlClass.isAbstract is True
        ]
        for clsName, clsDef in combDict.classes.items():
            if not (
                (clsDef.umlClass is None) == (clsName in API_ONLY_CLASSES)
                and (clsDef.ctClass is None) == (clsName in API_ONLY_CLASSES)
                and (clsDef.apiClass is not None or clsName in self.absCls)
            ):
                self.add_record(
                    cls=clsName,
                    api=clsDef.apiClass.obj_name if clsDef.apiClass else None,
                    ct=clsDef.ctClass.obj_name if clsDef.ctClass else None,
                    uml=clsDef.umlClass.obj_name if clsDef.umlClass else None,
                )
            else:
                if (
                    clsDef.umlClass
                    and clsDef.apiClass
                    and clsDef.umlClass.isAbstract
                    != clsDef.apiClass.isAbstract
                ):
                    self.add_record(
                        cls=clsName,
                        char="Abstract",
                        api=str(clsDef.apiClass.isAbstract),
                        uml=str(clsDef.umlClass.isAbstract),
                    )
                for prpName, prpDef in clsDef.properties.items():
                    if not (
                        (prpDef.umlProperty is None)
                        == (
                            clsName in API_ONLY_CLASSES
                            or prpName in API_ONLY_PROPERTIES
                            or (clsName, prpName) in API_ONLY_CLASS_PROPERTIES
                        )
                        and (prpDef.ctProperty is None)
                        == (
                            clsName in API_ONLY_CLASSES
                            or prpName
                            in API_ONLY_PROPERTIES + NON_CT_PROPERTIES
                            or (clsName, prpName) in API_ONLY_CLASS_PROPERTIES
                        )
                        and (prpDef.apiProperty or clsName in self.absCls)
                    ):
                        self.add_record(
                            cls=clsName,
                            attr=prpName,
                            api=prpDef.apiProperty.obj_name
                            if prpDef.apiProperty
                            else None,
                            ct=prpDef.ctProperty.obj_name
                            if prpDef.ctProperty
                            else None,
                            uml=prpDef.umlProperty.obj_name
                            if prpDef.umlProperty
                            else None,
                        )
                    else:
                        if prpDef.umlProperty and prpDef.ctProperty:
                            if (
                                prpDef.umlProperty.modelRepresentation
                                != prpDef.ctProperty.modelRepresentation
                            ):
                                self.add_record(
                                    cls=clsName,
                                    attr=prpName,
                                    char="CT Role/UML Representation",
                                    ct=prpDef.ctProperty.role,
                                    uml=prpDef.umlProperty.modelRepresentation,
                                )
                            elif any(
                                t
                                for t in prpDef.umlProperty.types
                                if t in combDict.classes
                            ) != (
                                prpDef.ctProperty.role
                                in [
                                    "Relationship",
                                    "Complex Datatype Relationship",
                                ]
                            ):
                                self.add_record(
                                    cls=clsName,
                                    attr=prpName,
                                    char="CT Role/UML Datatype",
                                    ct=prpDef.ctProperty.role,
                                    uml=format_value(prpDef.umlProperty.types),
                                )
                            if (
                                prpDef.umlProperty.inheritedFrom
                                != prpDef.ctProperty.inheritedFrom
                            ):
                                self.add_record(
                                    cls=clsName,
                                    attr=prpName,
                                    char="Inherited From",
                                    ct=prpDef.ctProperty.inheritedFrom,
                                    uml=prpDef.umlProperty.inheritedFrom,
                                )
                        if prpDef.umlProperty and prpDef.apiProperty:
                            if self.type_mismatches(
                                combDict=combDict, prpDef=prpDef
                            ):
                                self.add_record(
                                    cls=clsName,
                                    attr=prpName,
                                    char="Datatype(s)",
                                    api=format_value(
                                        sorted(prpDef.apiProperty.types)
                                    ),
                                    uml=format_value(
                                        sorted(prpDef.umlProperty.types)
                                    ),
                                )
                            if (
                                prpDef.umlProperty.cardinality
                                != prpDef.apiProperty.cardinality
                            ):
                                self.add_record(
                                    cls=clsName,
                                    attr=prpName,
                                    char="Cardinality",
                                    api=prpDef.apiProperty.cardinality,
                                    uml=prpDef.umlProperty.cardinality,
                                )

    def __repr__(self):
        return str(self.records)

    def add_record(
        self, cls, attr=None, char=None, api=None, ct=None, uml=None
    ):
        self.records.append(
            AlignmentRecord(
                cls=cls, attr=attr, char=char, api=api, ct=ct, uml=uml
            )
        )

    def write(self, csvFile: str = ALIGNMENT_FILE_NAME):
        csvfields = [v for v in ALIGNMENT_COLUMN_MAP.values()]
        with open(csvFile, "w", newline="") as f:
            w = csv.DictWriter(f, csvfields, extrasaction="ignore")
            w.writeheader()
            w.writerows(
                rowdicts=sorted(
                    [
                        {
                            ALIGNMENT_COLUMN_MAP[k]: v
                            for k, v in r.__dict__.items()
                        }
                        for r in self.records
                    ],
                    key=lambda d: d[ALIGNMENT_COLUMN_MAP["cls"]],
                )
            )

    def type_mismatches(
        self, combDict: ModelClassDict, prpDef: ModelClassProperty
    ):
        return not (
            (
                prpDef.relationshipType == "Ref"
                and prpDef.apiProperty.types == {"string"}
                and all(
                    t in combDict.classes for t in prpDef.umlProperty.types
                )
            )
            or (
                prpDef.relationshipType == "Value"
                and (
                    all(
                        ta == tu or (ta, tu) in VALID_API_UML_DATATYPES
                        for ta, tu in zip(
                            sorted(prpDef.apiProperty.types),
                            sorted(
                                t2
                                for t1 in [
                                    combDict.classes[t].umlClass.subClasses
                                    if t in combDict.classes
                                    and combDict.classes[t].umlClass
                                    is not None
                                    and combDict.classes[t].umlClass.isAbstract
                                    is True
                                    else [t]
                                    for t in prpDef.umlProperty.types
                                ]
                                for t2 in t1
                            ),
                        )
                    )
                )
            )
        )
