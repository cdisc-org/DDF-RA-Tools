from dataclasses import dataclass, field
from typing import Optional, Set
from ddf_ra_tools.model.descriptor import Descriptor


@dataclass
class UMLClassProperty(Descriptor):
    types: Set[str] = field(default_factory=lambda: set())
    cardinality: Optional[str] = None
    inheritedFrom: Optional[str] = None
    modelRepresentation: Optional[str] = None

    def __repr__(self):
        return super().__repr__()
