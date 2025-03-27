from typing import Union, Dict, List
from dataclasses import dataclass, field
from ddf_ra_tools.model.api_class import APIClassDict
from ddf_ra_tools.model.ct_class import CTClassDict
from ddf_ra_tools.model.uml_class import UMLClassDict
from ddf_ra_tools.utils import format_value
from ddf_ra_tools.config import DELTA_COLUMN_MAP, DELTA_CHARACTERISTIC_MAP
from copy import deepcopy
import csv
import yaml


@dataclass
class DeltaReport:
    clsDiffs: List = field(default_factory=lambda: [])

    def __init__(
        self,
        currDict: Union[Dict, APIClassDict, CTClassDict, UMLClassDict],
        prevDict: Union[Dict, APIClassDict, CTClassDict, UMLClassDict],
    ):
        self.clsDiffs = self.dict_compare(currDict.classes, prevDict.classes)

    @staticmethod
    def strip_prefix(s: str):
        for pfx in ["UML", "API", "CT"]:
            if s.startswith(pfx):
                return s[len(pfx) :]
        else:
            return s

    def get_dict_type(self, d):
        return self.strip_prefix(
            next(v for v in d.values()).__class__.__name__
            if isinstance(d, dict)
            else d.__class__.__name__
        )

    def get_diffs(self, o1, o2):
        diffs = {}
        if isinstance(o1, dict):
            diffs = self.dict_compare(
                o1, o2, self.get_dict_type(o1 or o2), "Name"
            )
        elif hasattr(o1, "__dict__"):
            diffs = self.dict_compare(
                o1.__dict__,
                o2.__dict__,
                self.get_dict_type(o1 or o2),
                "Property",
            )
        elif type(o1) in [set, list]:
            if sorted(o1) != sorted(o2):
                diffs = {"Old Value": sorted(o2), "New Value": sorted(o1)}
        elif o1 != o2:
            diffs = {"Old Value": o2, "New Value": o1}
        return diffs

    @staticmethod
    def get_label(dtype, itype, suffix=None):
        if suffix:
            return (
                "{} {}".format(dtype, suffix)
                if itype == "Name"
                else "{} {} {}".format(dtype, itype, suffix)
            )
        else:
            return "{} {}".format(
                dtype,
                itype,
            )

    def dict_compare(
        self,
        d1: Union[Dict, APIClassDict, CTClassDict, UMLClassDict],
        d2: Union[Dict, APIClassDict, CTClassDict, UMLClassDict],
        dtype: str = None,
        itype: str = "Name",
    ):
        dtype = dtype or self.get_dict_type(d1 or d2)
        d1_keys = set(d1.keys())
        d2_keys = set(d2.keys())
        shared_keys = d1_keys.intersection(d2_keys)
        changes = []
        if "obj_name" not in shared_keys:
            changes.extend(
                [
                    {
                        self.get_label(dtype, itype): DELTA_CHARACTERISTIC_MAP.get(k, k),
                        self.get_label(dtype, itype, "Status"): "Added",
                        "Diffs": self.get_diffs(
                            d1[k], d1[k].__class__(obj_name=k)
                        ),
                    }
                    for k in d1_keys - d2_keys
                ]
            )
            changes.extend(
                [
                    {
                        self.get_label(dtype, itype): DELTA_CHARACTERISTIC_MAP.get(k, k),
                        self.get_label(dtype, itype, "Status"): "Deleted",
                        "Diffs": self.get_diffs(
                            d2[k].__class__(obj_name=k), d2[k]
                        ),
                    }
                    for k in d2_keys - d1_keys
                ]
            )
        changes.extend(
            [
                {
                    self.get_label(dtype, itype): DELTA_CHARACTERISTIC_MAP.get(k, k),
                    self.get_label(dtype, itype, "Status"): "Modified",
                    "Diffs": self.get_diffs(d1[k], d2[k]),
                }
                for k in shared_keys
                if (
                    type(d1[k]) in [set, list]
                    and sorted(d1[k]) != sorted(d2[k])
                )
                or (type(d1[k]) not in [set, list] and d1[k] != d2[k])
            ]
        )

        return changes

    def recursive_write(self, writer: csv.DictWriter, difflist, diff={}):
        diffrow = deepcopy(diff)
        for subdiff in deepcopy(difflist):
            diffdetails = subdiff["Diffs"]
            subdiff.pop("Diffs")
            if isinstance(diffdetails, list):
                diffrow.update(subdiff)
                self.recursive_write(writer, diffdetails, diffrow)
            else:
                diffrow.update(subdiff)
                diffrow.update(
                    {
                        k: format_value(v)
                        for k, v in diffdetails.items()
                    }
                )
                writer.writerow(
                    {DELTA_COLUMN_MAP.get(k, k): v for k, v in diffrow.items()}
                )

    def to_csv(self, csvFile: str):
        csvfields = [v for v in DELTA_COLUMN_MAP.values()]
        with open(csvFile, "w", newline="") as f:
            w = csv.DictWriter(f, csvfields, extrasaction="ignore")
            w.writeheader()
            self.recursive_write(w, self.clsDiffs)

    def to_yaml(self, ymlFile: str):
        with open(ymlFile, "w", newline="") as f:
            yaml.dump(self.clsDiffs, f, sort_keys=False)
