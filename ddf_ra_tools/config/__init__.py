import inflect

inflect_engine = inflect.engine()
# TODO: replace with values read in from config file
inflect_engine.defnoun("previous", "previous")
inflect_engine.defnoun("context", "context")
inflect_engine.defnoun("to", "to")
inflect_engine.defnoun("of", "of")
inflect_engine.defnoun("category", "categories")

API_ROOT_SCHEMA = "Study-Output"
API_ONLY_CLASSES = ["ExtensionClass", "ExtensionAttribute"]
API_ONLY_PROPERTIES = ["instanceType", "extensionAttributes"]
API_ONLY_CLASS_PROPERTIES = [
    ("InterventionalStudyDesign", "analysisPopulations"),
    ("InterventionalStudyDesign", "eligibilityCriteria"),
    ("ObservationalStudyDesign", "analysisPopulations"),
    ("ObservationalStudyDesign", "eligibilityCriteria"),
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
}
