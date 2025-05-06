from dataclasses import dataclass, field
from typing import List, Dict
from ddf_ra_tools.model.model_class import ModelClassDict, ModelClass
from ddf_ra_tools.model.model_class_property import ModelClassProperty
from ddf_ra_tools.config import (
    TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES,
    TEST_DATA_TEMPLATE_EXCLUDE_PROPERTIES,
    TEST_DATA_TEMPLATE_FILE_NAME,
    TEST_DATA_TEMPLATE_PRIMITIVE_DATA_TYPES,
    TEST_DATA_TEMPLATE_TYPE_MAP,
)
import re
import xlsxwriter


@dataclass
class TestDataTemplatePropertyRecord:
    name: str
    label: str
    dtype: str
    card: str


@dataclass
class TestDataTemplateClassRecord:
    fromModel: ModelClassDict
    fromClass: ModelClass
    datasetName: str
    datasetLabel: str
    fileName: str
    attributes: List[TestDataTemplatePropertyRecord] = field(
        default_factory=lambda: []
    )

    def get_description(
        self, clsName: str, prpDef: ModelClassProperty = None
    ) -> str:
        return "{}{}".format(
            prpDef.ctProperty.preferredTerm
            if prpDef.ctProperty and prpDef.ctProperty.preferredTerm
            else "({} {})".format(
                self.name_to_desc(clsName), self.name_to_desc(prpDef.obj_name)
            ),
            " [Identifier{}]".format(
                "" if prpDef.cardinality.endswith("1") else "s"
            )
            if prpDef.relationshipType == "Ref"
            else "",
        )

    @staticmethod
    def name_to_desc(objName: str) -> str:
        return re.sub("([A-Z]+)", r" \1", objName).strip().title()

    def get_cardinality(self, prpDef: ModelClassProperty) -> str:
        return (
            " / ".join(
                "{}[{}]".format(t, prpDef.cardinality)
                for t in self.get_types(prpDef)
            )
            if prpDef.relationshipType == "Value"
            else "{}[{}] ({})".format(
                "".join(prpDef.apiProperty.types),
                prpDef.cardinality,
                " / ".join([t + ".id" for t in self.get_types(prpDef)]),
            )
        )

    def is_complex_datatype(self, types: List) -> bool:
        return any(t in self.fromModel.classes for t in types)

    def get_types(self, prpDef: ModelClassProperty):
        return sorted(
            t2
            for t1 in [
                self.fromModel.classes[t].umlClass.subClasses
                if t in self.fromModel.classes
                and self.fromModel.classes[t].modifier == "Abstract"
                else [t]
                for t in prpDef.types
            ]
            for t2 in t1
        )

    def get_properties(
        self,
        mdlClsName: str,
        parentPath: List[TestDataTemplatePropertyRecord] = [],
    ):
        mdlClsDef: ModelClass = self.fromModel.classes[mdlClsName]
        if mdlClsDef.umlClass and mdlClsDef.umlClass.superClasses:
            for sc in mdlClsDef.umlClass.subClasses:
                self.get_properties(mdlClsName=sc, parentPath=parentPath)
        for mdlPrpDef in mdlClsDef.properties.values():
            if mdlPrpDef.apiProperty:
                mdlPrpName = mdlPrpDef.apiProperty.obj_name
                if mdlPrpName in TEST_DATA_TEMPLATE_EXCLUDE_PROPERTIES:
                    print(
                        "Ignoring excluded {} attribute: {}".format(
                            self.fromClass.obj_name,
                            ".".join(
                                [p.name for p in parentPath] + [mdlPrpName]
                            ),
                        )
                    )

                elif (
                    mdlPrpName,
                    " / ".join(sorted(mdlPrpDef.apiProperty.types)),
                ) in [(p.name, p.dtype) for p in parentPath]:
                    print(
                        "Circular relationship in {}: {} contains {}".format(
                            self.fromClass.obj_name,
                            ".".join(p.name for p in parentPath),
                            mdlPrpName,
                        )
                    )
                else:
                    prpDesc = self.get_description(
                        clsName=mdlClsName, prpDef=mdlPrpDef
                    )
                    if self.is_complex_datatype(
                        mdlPrpDef.apiProperty.types
                    ) or not mdlPrpDef.cardinality.endswith("1"):
                        self.attributes.append(
                            TestDataTemplatePropertyRecord(
                                name=".".join(
                                    [p.name for p in parentPath] + [mdlPrpName]
                                ),
                                label="{} [{}]".format(
                                    " / ".join(
                                        [p.label for p in parentPath]
                                        + [prpDesc]
                                    ),
                                    "Exists"
                                    if mdlPrpDef.cardinality.endswith("1")
                                    else "Any Exist",
                                ),
                                dtype="Boolean",
                                card=self.get_cardinality(prpDef=mdlPrpDef),
                            ),
                        )
                    if mdlPrpDef.cardinality.endswith("1"):
                        for ptype in sorted(mdlPrpDef.apiProperty.types):
                            prpDef = TestDataTemplatePropertyRecord(
                                name=mdlPrpName,
                                label=prpDesc,
                                dtype=" / ".join(
                                    sorted(mdlPrpDef.apiProperty.types)
                                ),
                                card="{}[{}]".format(
                                    ptype, mdlPrpDef.cardinality
                                ),
                            )
                            path = parentPath + [prpDef]
                            if ptype in self.fromModel.classes:
                                self.get_properties(
                                    mdlClsName=ptype, parentPath=path
                                )
                            else:
                                self.attributes.append(
                                    TestDataTemplatePropertyRecord(
                                        name=".".join(p.name for p in path),
                                        label=" / ".join(
                                            p.label for p in path
                                        ),
                                        dtype=TEST_DATA_TEMPLATE_TYPE_MAP.get(
                                            ptype, ptype
                                        ).title(),
                                        card="{}[{}]{}".format(
                                            ">".join(
                                                [p.card for p in parentPath]
                                                + [mdlPrpName]
                                            )
                                            if parentPath
                                            else "",
                                            mdlPrpDef.cardinality,
                                            " ({})".format(
                                                " / ".join(
                                                    t + ".id"
                                                    for t in self.get_types(
                                                        mdlPrpDef
                                                    )
                                                )
                                            )
                                            if mdlPrpDef.relationshipType
                                            == "Ref"
                                            else "",
                                        ),
                                    )
                                )


@dataclass
class TestDataTemplateReport:
    report: Dict[str, TestDataTemplateClassRecord] = field(
        default_factory=lambda: {}
    )
    mdlVersion: str = None

    def __init__(self, combDict: ModelClassDict):
        self.report = {}
        self.mdlVersion = combDict.version
        for (clsName, clsDef) in [
            (k, v)
            for k, v in combDict.classes.items()
            if v.modifier != "Abstract"
        ]:
            self.report[clsName] = TestDataTemplateClassRecord(
                fromModel=combDict,
                fromClass=clsDef,
                datasetName=clsName,
                datasetLabel=clsDef.ctClass.preferredTerm
                if clsDef.ctClass
                else clsName,
                fileName="{}.xpt".format(
                    clsName if len(clsName) <= 27 else clsName[:27]
                ),
                attributes=[
                    TestDataTemplatePropertyRecord(**sp)
                    for sp in TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES
                ],
            )

            self.report[clsName].get_properties(mdlClsName=clsName)

    def write(self, xlFile: str = TEST_DATA_TEMPLATE_FILE_NAME):
        workbook = xlsxwriter.Workbook(xlFile)
        workbook.set_custom_property("USDM Version", str(self.mdlVersion))

        header = workbook.add_format()
        header.set_bold()
        header.set_align("top")
        header.set_text_wrap()

        sub_header = workbook.add_format()
        sub_header.set_italic()
        sub_header.set_bg_color("#FFFFCC")
        sub_header.set_text_wrap()
        sub_header.set_align("top")

        normal = workbook.add_format()
        normal.set_align("top")
        normal.set_num_format("@")

        duplicate = workbook.add_format()
        duplicate.set_bg_color("#FFC7CE")
        duplicate.set_font_color("#9C0006")

        dsws = workbook.add_worksheet("Datasets")
        dsprps = ["Filename", "Dataset Name", "Label"]
        dsws.set_column(0, len(dsprps), 30)
        dsws.write_row(0, 0, dsprps, header)

        clsn = 0

        for clsRpt in self.report.values():
            clsn += 1
            dsws.write_url(
                clsn,
                0,
                f"internal:'{clsRpt.fileName}'!A1",
                string=clsRpt.fileName,
            )
            dsws.write_row(clsn, 1, [clsRpt.datasetName, clsRpt.datasetLabel])
            ws = workbook.add_worksheet(clsRpt.fileName)
            ws.set_column(0, len(clsRpt.attributes), 25)
            ws.conditional_format(
                0,
                0,
                0,
                len(clsRpt.attributes) - 1,
                {"type": "duplicate", "format": duplicate},
            )
            ws.write_row(0, 0, [p.name for p in clsRpt.attributes], header)
            ws.write_row(
                1, 0, [p.label for p in clsRpt.attributes], sub_header
            )
            ws.write_row(
                2, 0, [p.dtype for p in clsRpt.attributes], sub_header
            )
            ws.write_row(3, 0, [p.card for p in clsRpt.attributes], sub_header)
            # Add a blank row with defined format to prevent auto-copying of
            # format from row above.
            ws.write_row(4, 0, [None] * len(clsRpt.attributes), normal)

        for pdtype in TEST_DATA_TEMPLATE_PRIMITIVE_DATA_TYPES:
            clsn += 1
            dsname = pdtype
            dsws.write_url(
                clsn, 0, f"internal:'{dsname}.xpt'!A1", string=f"{dsname}.xpt"
            )
            dsws.write_row(clsn, 1, [dsname, f"{pdtype.title()} Values"])
            ws = workbook.add_worksheet(f"{dsname}.xpt")
            ws.set_column(0, 4, 25)
            ws.write_row(
                0,
                0,
                [p["name"] for p in TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES]
                + ["value"],
                header,
            )
            ws.write_row(
                1,
                0,
                [p["label"] for p in TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES]
                + [
                    "Value",
                ],
                sub_header,
            )
            ws.write_row(
                2,
                0,
                [p["dtype"] for p in TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES]
                + ["String"],
                sub_header,
            )
            ws.write_row(
                3,
                0,
                [p["card"] for p in TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES]
                + ["[0]" if pdtype == "null" else "[1]"],
                sub_header,
            )
            # Add a blank row with defined format to prevent auto-copying of
            # format from row above.
            ws.write_row(
                4,
                0,
                [None] * (len(TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES) + 1),
                normal,
            )

        workbook.close()
