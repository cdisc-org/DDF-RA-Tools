from dataclasses import dataclass, field
from typing import Optional, List
from ddf_ra_tools.model.model_class import ModelClassDict
from ddf_ra_tools.utils import format_value
from ddf_ra_tools.config import DATA_DICTIONARY_COLUMN_MAP


@dataclass
class DataDictionaryRecord:
    cls: Optional[str] = None
    attr: Optional[str] = None
    dtyp: Optional[str] = None
    ncic: Optional[str] = None
    card: Optional[str] = None
    ptrm: Optional[set] = None
    defn: Optional[str] = None
    cref: Optional[str] = None
    ifrm: Optional[str] = None

    def __repr__(self):
        return "|{}|".format(
            "|".join(
                [
                    self.__dict__[k] if self.__dict__[k] else ""
                    for k in DATA_DICTIONARY_COLUMN_MAP.keys()
                ]
            )
        )


@dataclass
class DataDictionaryReport:
    records: List[DataDictionaryRecord] = field(default_factory=lambda: [])

    def __init__(self, combDict: ModelClassDict):
        self.records = []
        self.add_record(**DATA_DICTIONARY_COLUMN_MAP)
        self.add_record(
            **{k: "---" for k in DATA_DICTIONARY_COLUMN_MAP.keys()}
        )
        for clsName, clsDef in combDict.classes.items():
            if clsDef.umlClass is not None:
                self.add_record(
                    cls=clsName,
                    ncic=clsDef.ctClass.defNciCode if clsDef.ctClass else None,
                    ptrm=clsDef.ctClass.preferredTerm
                    if clsDef.ctClass
                    else None,
                    defn=clsDef.ctClass.definition if clsDef.ctClass else None,
                )
                for prpName, prpDef in clsDef.properties.items():
                    if prpDef.umlProperty is not None:
                        self.add_record(
                            attr=prpName,
                            dtyp=prpDef.types,
                            ncic=prpDef.ctProperty.defNciCode
                            if prpDef.ctProperty
                            else None,
                            card=prpDef.cardinality,
                            ptrm=prpDef.ctProperty.preferredTerm
                            if prpDef.ctProperty
                            else None,
                            defn=prpDef.ctProperty.definition
                            if prpDef.ctProperty
                            else None,
                            cref=prpDef.ctProperty.codelistReference
                            if prpDef.ctProperty
                            else None,
                            ifrm=prpDef.umlProperty.inheritedFrom
                            or prpDef.ctProperty.inheritedFrom
                            if prpDef.ctProperty
                            else None,
                        )

    def add_record(
        self,
        cls=None,
        attr=None,
        dtyp=None,
        ncic=None,
        card=None,
        ptrm=None,
        defn=None,
        cref=None,
        ifrm=None,
    ):
        self.records.append(
            DataDictionaryRecord(
                cls=cls,
                attr=attr,
                dtyp=format_value(dtyp),
                ncic=ncic,
                card=card,
                ptrm=ptrm,
                defn=defn,
                cref=cref,
                ifrm=ifrm,
            )
        )

    def to_md(self, mdFile):
        with open(mdFile, "w") as f:
            f.writelines([repr(r) + "\n" for r in self.records])
