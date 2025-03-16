from typing import Dict

from bs4 import BeautifulSoup, Tag

from ddf_ra_tools.model.uml_class import UMLClass, UMLClassDict
from ddf_ra_tools.model.uml_class_property import UMLClassProperty
from ddf_ra_tools.utils import get_card, add_sub_classes


class XMIParser:
    def __init__(self, xmiFile: str):
        self.xmiFile = xmiFile
        with open(xmiFile) as f:
            xmidata = f.read()
        self.xmi = BeautifulSoup(xmidata, "lxml-xml")

    def get_model(self) -> UMLClassDict:
        mdl: UMLClassDict = UMLClassDict(
            source=self.xmiFile, version=self._get_model_version()
        )
        for clsNode in self.xmi.find_all(
            "packagedElement", attrs={"xmi:type": "uml:Class"}
        ):
            clsName = clsNode["name"]
            clsDef = UMLClass(
                obj_name=clsName,
                isAbstract=bool(clsNode["isAbstract"])
                if clsNode.has_attr("isAbstract")
                else False,
                superClasses=[],
                subClasses=[],
                properties={},
            )

            if clsNode.generalization:
                for gen in clsNode.find_all("generalization"):
                    gclsNode = self._get_class_node_by_id(gen["general"])
                    gclsName = gclsNode["name"]
                    clsDef.superClasses.append(gclsName)
                    self._get_attrs(
                        clsNode=gclsNode,
                        props=clsDef.properties,
                        inheritedFrom=gclsName,
                    )
                    self._get_rels(
                        clsNode=gclsNode,
                        props=clsDef.properties,
                        inheritedFrom=gclsName,
                    )
            self._get_attrs(clsNode=clsNode, props=clsDef.properties)
            self._get_rels(clsNode=clsNode, props=clsDef.properties)
            mdl.classes.update({clsName: clsDef})

        add_sub_classes(mdl)

        return mdl

    def _get_attrs(
        self,
        clsNode: Tag,
        props: Dict[str, UMLClassProperty],
        inheritedFrom: str = None,
    ):
        for attrNode in (
            x
            for x in clsNode.find_all(
                "ownedAttribute", attrs={"xmi:type": "uml:Property"}
            )
            if x.has_attr("name")
        ):
            attrName = attrNode["name"]
            attrId = str(attrNode["xmi:id"])
            attrDef = self.xmi.find("attribute", attrs={"xmi:idref": attrId})
            props[attrName] = UMLClassProperty(
                obj_name=attrName,
                types={attrDef.properties["type"]},
                cardinality=get_card(
                    cardLow=attrDef.bounds["lower"],
                    cardHigh=attrDef.bounds["upper"],
                ),
                inheritedFrom=inheritedFrom,
                modelRepresentation="Attribute",
            )

    def _get_rels(
        self,
        clsNode: Tag,
        props: Dict[str, UMLClassProperty],
        inheritedFrom: str = None,
    ):
        for relNode in (
            x.find_parent("connector")
            for x in self.xmi.find_all(
                "source", attrs={"xmi:idref": clsNode["xmi:id"]}
            )
            if x.find_parent("connector").has_attr("name")
        ):
            relName = relNode["name"]
            tgtName = self._get_class_node_by_id(relNode.target["xmi:idref"])[
                "name"
            ]
            tgtCard = relNode.target.type.get("multiplicity")
            if relName in props:
                props[relName].types.update({tgtName})
            else:
                props[relName] = UMLClassProperty(
                    obj_name=relName,
                    types={tgtName},
                    cardinality=tgtCard,
                    inheritedFrom=inheritedFrom,
                    modelRepresentation="Relationship",
                )

    def _get_class_node_by_id(self, clsId: str) -> Tag:
        return self.xmi.find(
            "packagedElement",
            attrs={
                "xmi:type": "uml:Class",
                "xmi:id": clsId,
            },
        )

    def _get_model_version(self):
        return (
            self.xmi.find("properties", {"name": "USDM", "type": "Logical"})
            .find_parent("diagram")
            .project["version"]
        )
