from dataclasses import dataclass
from typing import Optional
from ddf_ra_tools.model.descriptor import Descriptor


@dataclass
class CTDescriptor(Descriptor):
    defNciCode: Optional[str] = None
    definition: Optional[str] = None
    preferredTerm: Optional[str] = None

    def __repr__(self):
        return super().__repr__()

    def __eq__(self, other):
        return super().__eq__(other)
