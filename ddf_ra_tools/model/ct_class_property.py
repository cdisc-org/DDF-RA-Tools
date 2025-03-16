from dataclasses import dataclass
from typing import Optional
from ddf_ra_tools.model.ct_descriptor import CTDescriptor


@dataclass
class CTClassProperty(CTDescriptor):
    role: Optional[str] = None
    modelRepresentation: Optional[str] = None
    inheritedFrom: Optional[str] = None
    hasValueList: Optional[str] = None
    codelistReference: Optional[str] = None
    codelistUrl: Optional[str] = None

    def __post_init__(self):
        self.modelRepresentation = (
            "Attribute"
            if self.role == "Complex Datatype Relationship"
            else self.role
        )

    def __repr__(self):
        return super().__repr__()

    def __eq__(self, other):
        return super().__eq__(other)
