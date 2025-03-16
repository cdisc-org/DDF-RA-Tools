from dataclasses import dataclass, field
from typing import Dict
from ddf_ra_tools.model.descriptor import Descriptor
from ddf_ra_tools.model.api_class_property import APIClassProperty


@dataclass
class APIClass(Descriptor):
    isAbstract: bool = False
    properties: Dict[str, APIClassProperty] = field(default_factory=lambda: {})

    def __repr__(self):
        return super().__repr__()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


@dataclass
class APIClassDict:
    source: str
    version: str
    classes: Dict[str, APIClass] = field(default_factory=lambda: {})
