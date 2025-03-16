from dataclasses import dataclass, field
from typing import List, Dict
from ddf_ra_tools.model.ct_descriptor import CTDescriptor
from ddf_ra_tools.model.ct_class_property import CTClassProperty


@dataclass
class CTClass(CTDescriptor):
    properties: Dict[str, CTClassProperty] = field(default_factory=lambda: {})
    superClasses: List[str] = field(default_factory=lambda: [])
    subClasses: List[str] = field(default_factory=lambda: [])

    def __repr__(self):
        return super().__repr__()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


@dataclass
class CTClassDict:
    source: str
    version: str
    classes: Dict[str, CTClass] = field(default_factory=lambda: {})
