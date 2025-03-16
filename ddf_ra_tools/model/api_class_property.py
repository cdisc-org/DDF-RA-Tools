from dataclasses import dataclass, field
from typing import Optional, Set
from ddf_ra_tools.model.descriptor import Descriptor

import re
from ddf_ra_tools.config import inflect_engine


@dataclass
class APIClassProperty(Descriptor):
    types: Set[str] = field(default_factory=lambda: set())
    cardinality: Optional[str] = None
    synonyms: Set[str] = field(default_factory=lambda: set())

    def __post_init__(self):
        nameParts = re.findall(r"([A-Z]?[a-z]+)", self.obj_name.strip())
        if nameParts[-1] in ["Id", "Ids"]:
            self.synonyms.update({"".join(nameParts[0:-1])})
            if nameParts[-1] == "Ids":
                self.synonyms.update(
                    {
                        "".join(
                            nameParts[0:-2]
                            + [inflect_engine.plural_noun(nameParts[-2])]
                        )
                    }
                )

    def __repr__(self):
        return super().__repr__()

    def __eq__(self, other):
        return super().__eq__(other)
