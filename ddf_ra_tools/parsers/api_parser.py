import json
from jsonpath_ng.ext import parse

from ddf_ra_tools.model.api_class import APIClass, APIClassDict
from ddf_ra_tools.model.api_class_property import APIClassProperty

from ddf_ra_tools.config import API_ROOT_SCHEMA


class APIParser:
    def __init__(self, apiFile: str):
        self.apiFile = apiFile
        with open(apiFile) as f:
            self.apischema = json.load(f)
        self.schemas = {
            k: v
            for k, v in self.apischema.get("components").get("schemas").items()
        }

    def get_model(self) -> APIClassDict:
        self.mdl: APIClassDict = APIClassDict(
            source=self.apiFile,
            version=self._get_model_version(),
            classes={},
        )
        self.add_classes(set({f"#/components/schemas/{API_ROOT_SCHEMA}"}))
        return self.mdl

    def add_classes(self, schemaRefs: set):
        for schemaRef in schemaRefs:
            schemaName = schemaRef.replace("#/components/schemas/", "")
            subSchemas = set()
            if schemaName in self.schemas:
                clsSchema = self.schemas[schemaName]
                clsName = clsSchema.get("title")
                if clsName not in self.mdl.classes:
                    self.mdl.classes[clsName] = APIClass(
                        obj_name=clsName,
                        isAbstract=False,
                        properties={
                            pn: self.get_property(
                                propName=pn,
                                propDef=pv,
                                context=clsSchema,
                                subSchemas=subSchemas,
                            )
                            for pn, pv in clsSchema.get("properties").items()
                        },
                    )
            self.add_classes(subSchemas)

    def get_property(
        self, propName, propDef, context, subSchemas: set
    ) -> APIClassProperty:
        return APIClassProperty(
            obj_name=propName,
            types=self._get_types(propDef, subSchemas),
            cardinality=self._get_card(propName, propDef, context),
        )

    def _get_model_version(self):
        return parse("$.info.version").find(self.apischema)[0].value

    def _get_types(self, propDef, subSchemas: set):
        typelist = set()
        self._build_type_list(propDef, typelist, subSchemas)
        return typelist

    def _build_type_list(self, propDef: dict, types: set, subSchemas: set):
        propType = propDef.get("type")
        propConst = propDef.get("const")
        propAnyOf = propDef.get("anyOf")
        propRef = propDef.get("$ref")
        if propType:
            if propType == "array":
                self._build_type_list(propDef.get("items"), types, subSchemas)
            else:
                types.add(propType)
        elif propConst:
            types.add("string")
        elif propAnyOf:
            for t in propAnyOf:
                if not ("type" in t and t["type"] == "null"):
                    self._build_type_list(t, types, subSchemas)
        elif propRef:
            subSchemas.update({propRef})
            types.add(self._ref_to_type(propRef))

    def _ref_to_type(self, ref: str):
        return self.schemas.get(ref.replace("#/components/schemas/", ""))[
            "title"
        ]

    def _get_card(self, propName: str, propDef: dict, context: dict):
        propType = propDef.get("type")
        propConst = propDef.get("const")
        propDflt = propDef.get("default")
        propReq = context.get("required", [])
        propAnyOf = propDef.get("anyOf", [])
        if propConst:
            return "1"
        elif propType == "array":
            minCard = propDef.get(
                "minItems",
                "0"
                if propName not in propReq and isinstance(propDflt, list)
                else "1",
            )
            maxCard = propDef.get("maxItems", "*")
            return "{}..{}".format(minCard, maxCard)
        else:
            minLength = propDef.get("minLength")
            if not (propName in propReq or minLength) or any(
                t for t in propAnyOf if "type" in t and t["type"] == "null"
            ):
                return "0..1"
            else:
                return "1"
