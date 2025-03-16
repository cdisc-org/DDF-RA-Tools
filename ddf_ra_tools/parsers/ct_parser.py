import openpyxl
import re

from ddf_ra_tools.model.ct_class import CTClass, CTClassDict
from ddf_ra_tools.model.ct_class_property import CTClassProperty
from ddf_ra_tools.utils import add_sub_classes


class CTParser:
    def __init__(self, ctFile: str, version: str):
        self.ctFile = ctFile
        self.version = version
        ctwb = openpyxl.load_workbook(filename=ctFile, data_only=True)
        self.ctws = ctwb["DDF Entities&Attributes"]
        self.ctcolmap = {
            ctcol.value: ctcol.column - 1 for ctcol in tuple(self.ctws.rows)[0]
        }

    def get_model(self) -> CTClassDict:
        mdl: CTClassDict = CTClassDict(
            source=self.ctFile, version=self.version
        )

        for ctrow in self.ctws.iter_rows(min_row=2):
            entName = ctrow[self.ctcolmap["Entity Name"]].value
            elrole = ctrow[self.ctcolmap["Role"]].value
            elname = ctrow[self.ctcolmap["Logical Data Model Name"]].value
            elinfrom = ctrow[self.ctcolmap["Inherited From"]].value
            if elrole == "Entity":
                if elname != entName:
                    print(
                        f"Entity Name '{entName}' does not match Logical Data "
                        + f"Model Name for Entity '{elname}'"
                    )
                mdl.classes.update(
                    {
                        entName: CTClass(
                            obj_name=entName,
                            defNciCode=ctrow[
                                self.ctcolmap["NCI C-code"]
                            ].value,
                            preferredTerm=ctrow[
                                self.ctcolmap["CT Item Preferred Name"]
                            ].value,
                            definition=ctrow[
                                self.ctcolmap["Definition"]
                            ].value,
                            superClasses=[elinfrom] if elinfrom else [],
                            properties={},
                        )
                    }
                )
            else:
                cref: str = None
                cref = re.search(
                    r"^Y \((.+?)\)$",
                    str(ctrow[self.ctcolmap["Has Value List"]].value).strip(),
                )
                mdl.classes[entName].properties.update(
                    {
                        elname: CTClassProperty(
                            obj_name=elname,
                            defNciCode=ctrow[
                                self.ctcolmap["NCI C-code"]
                            ].value,
                            preferredTerm=ctrow[
                                self.ctcolmap["CT Item Preferred Name"]
                            ].value,
                            definition=ctrow[
                                self.ctcolmap["Definition"]
                            ].value,
                            role=elrole,
                            inheritedFrom=elinfrom,
                            hasValueList=cref.group(0)
                            if cref
                            else ctrow[self.ctcolmap["Has Value List"]].value,
                            codelistReference=cref.group(1) if cref else None,
                            codelistUrl=ctrow[
                                self.ctcolmap["Codelist URL"]
                            ].value,
                        )
                    }
                )
                if (
                    elinfrom
                    and elinfrom not in mdl.classes[entName].superClasses
                ):
                    mdl.classes[entName].superClasses.append(elinfrom)

        add_sub_classes(mdl)

        return mdl
