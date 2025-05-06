import os
import inflect

inflect_engine = inflect.engine()

# The following are custom singular/plural noun combinations that
# are used to derive valid API ...Id/...Ids attribute synonyms when
# inflect's default singular/plural conversion is not sufficient.
# Add new definitions in the form:
#
#   inflect_engine.defnoun("<singular form>", "<plural form>")
#
# Note that both <singular form> and <plural form> should be in lower case.
# Only the last part of compound attribute names needs to be defined.
# For example, for an attribute called "multiPartAttrib", a new noun
# would only need to be defined for "attrib".

inflect_engine.defnoun("previous", "previous")
inflect_engine.defnoun("context", "context")
inflect_engine.defnoun("to", "to")
inflect_engine.defnoun("of", "of")
inflect_engine.defnoun("category", "categories")

UML_FILE_NAME = "USDM_UML.xmi"
CT_FILE_NAME = "USDM_CT.xlsx"
API_FILE_NAME = "USDM_API.json"

PREV_RELEASE_FOLDER_NAME = os.path.join("resources", "prevRelease")
CURR_RELEASE_FOLDER_NAME = os.path.join("resources", "currRelease")

UML_DELTA_FILE_ROOT = "UML_DELTA"
CT_DELTA_FILE_ROOT = "CT_DELTA"
API_DELTA_FILE_ROOT = "API_DELTA"

DATA_DICTIONARY_FILE_NAME = "dataDictionary.MD"
DATA_STRUCTURE_FILE_NAME = "dataStructure.yml"
ALIGNMENT_FILE_NAME = "alignment.csv"
TEST_DATA_TEMPLATE_FILE_NAME = "CORE Test Data Template.xlsx"

API_ROOT_SCHEMA = "Study-Output"
API_ONLY_CLASSES = ["ExtensionClass", "ExtensionAttribute"]
API_ONLY_PROPERTIES = ["instanceType", "extensionAttributes"]
API_ONLY_CLASS_PROPERTIES = [
    ("InterventionalStudyDesign", "analysisPopulations"),
    ("ObservationalStudyDesign", "analysisPopulations"),
    ("StudyVersion", "conditions"),
    ("StudyVersion", "studyInterventions"),
    ("StudyVersion", "bcSurrogates"),
    ("StudyVersion", "roles"),
    ("StudyVersion", "administrableProducts"),
    ("StudyVersion", "productOrganizationRoles"),
    ("StudyVersion", "narrativeContentItems"),
    ("StudyVersion", "eligibilityCriterionItems"),
    ("StudyVersion", "organizations"),
    ("StudyVersion", "bcCategories"),
    ("StudyVersion", "medicalDevices"),
    ("StudyVersion", "dictionaries"),
    ("StudyVersion", "biomedicalConcepts"),
]
NON_CT_PROPERTIES = ["id"]
VALID_API_UML_DATATYPES = [
    ("string", "Date"),
    ("string", "String"),
    ("boolean", "Boolean"),
    ("number", "Float"),
]
ALIGNMENT_COLUMN_MAP = {
    "cls": "Class",
    "attr": "Attribute",
    "char": "Characteristic",
    "api": "API",
    "ct": "CT",
    "uml": "UML / DD",
}

DELTA_COLUMN_MAP = {
    "Class Name": "Class Name",
    "Class Status": "Class Status",
    "Class Property": "Class Characteristic",
    "ClassProperty Name": "Attribute/Relationship Name",
    "ClassProperty Status": "Attribute/Relationship Status",
    "ClassProperty Property": "Attribute/Relationship Characteristic",
    "Old Value": "Old Value",
    "New Value": "New Value",
}

DELTA_CHARACTERISTIC_MAP = {
    "isAbstract": "Abstract",
    "defNciCode": "NCI C-Code",
    "preferredTerm": "Preferred Term",
    "definition": "Definition",
    "superClasses": "Super Classes",
    "subClasses": "Sub Classes",
    "properties": "Attributes/Relationships",
    "types": "Data Type",
    "role": "Role",
    "modelRepresentation": "Model Representation",
    "cardinality": "Cardinality",
    "hasValueList": "Has Value List",
    "codelistReference": "Codelist Ref",
    "codelistUrl": "Codelist URL",
    "inheritedFrom": "Inherited From",
}

DATA_DICTIONARY_COLUMN_MAP = {
    "cls": "Class Name",
    "attr": "Attribute Name",
    "dtyp": "Data Type",
    "ncic": "NCI C-Code",
    "card": "Cardinality",
    "ptrm": "Preferred Term",
    "defn": "Definition",
    "cref": "Codelist Ref",
    "ifrm": "Inherited From",
}

DATA_STRUCTURE_CLASS_KEY_MAP = {
    "defNciCode": "NCI C-Code",
    "preferredTerm": "Preferred Term",
    "definition": "Definition",
    "modifier": "Modifier",
    "superClasses": "Super Classes",
    "subClasses": "Sub Classes",
    "attributes": "Attributes",
}

DATA_STRUCTURE_PROPERTY_KEY_MAP = {
    "types": "Type",
    "defNciCode": "NCI C-Code",
    "preferredTerm": "Preferred Term",
    "definition": "Definition",
    "cardinality": "Cardinality",
    "relationshipType": "Relationship Type",
    "modelName": "Model Name",
    "modelRepresentation": "Model Representation",
    "inheritedFrom": "Inherited From",
}

TEST_DATA_TEMPLATE_SYSTEM_PROPERTIES = [
    {
        "name": "parent_entity",
        "label": "Parent Entity Name",
        "dtype": "String",
        "card": "[1]",
    },
    {
        "name": "parent_id",
        "label": "Parent Entity Id",
        "dtype": "String",
        "card": "[1]",
    },
    {
        "name": "parent_rel",
        "label": "Name of Relationship from Parent Entity",
        "dtype": "String",
        "card": "[1]",
    },
    {
        "name": "rel_type",
        "label": "Type of Relationship",
        "dtype": "String",
        "card": "[1]",
    },
]

TEST_DATA_TEMPLATE_EXCLUDE_PROPERTIES = ["extensionAttributes"]

TEST_DATA_TEMPLATE_PRIMITIVE_DATA_TYPES = ["string", "float", "boolean", "null"]

TEST_DATA_TEMPLATE_TYPE_MAP = {"number": "float"}