import os

from ddf_ra_tools.parsers.xmi_parser import XMIParser
from ddf_ra_tools.parsers.api_parser import APIParser
from ddf_ra_tools.parsers.ct_parser import CTParser

from ddf_ra_tools.config import (
    CURR_RELEASE_FOLDER_NAME,
    PREV_RELEASE_FOLDER_NAME,
    UML_FILE_NAME,
    CT_FILE_NAME,
    API_FILE_NAME,
    UML_DELTA_FILE_ROOT,
    CT_DELTA_FILE_ROOT,
    API_DELTA_FILE_ROOT,
)

from ddf_ra_tools.model.model_class import ModelClassDict

from ddf_ra_tools.reports.data_structure import DataStructureReport
from ddf_ra_tools.reports.data_dictionary import DataDictionaryReport
from ddf_ra_tools.reports.alignment import AlignmentReport
from ddf_ra_tools.reports.delta import DeltaReport

currXMI = XMIParser(
    os.path.join(CURR_RELEASE_FOLDER_NAME, UML_FILE_NAME)
).get_model()
prevXMI = XMIParser(
    os.path.join(PREV_RELEASE_FOLDER_NAME, UML_FILE_NAME)
).get_model()

DeltaReport(currDict=currXMI, prevDict=prevXMI).to_csv(
    f"{UML_DELTA_FILE_ROOT}.csv"
)

currAPI = APIParser(
    os.path.join(CURR_RELEASE_FOLDER_NAME, API_FILE_NAME)
).get_model()
prevAPI = APIParser(
    os.path.join(PREV_RELEASE_FOLDER_NAME, API_FILE_NAME)
).get_model()

DeltaReport(currDict=currAPI, prevDict=prevAPI).to_csv(
    f"{API_DELTA_FILE_ROOT}.csv"
)

currCT = CTParser(
    ctFile=os.path.join(CURR_RELEASE_FOLDER_NAME, CT_FILE_NAME),
    version=currAPI.version,
).get_model()
prevCT = CTParser(
    ctFile=os.path.join(PREV_RELEASE_FOLDER_NAME, CT_FILE_NAME),
    version=prevAPI.version,
).get_model()

DeltaReport(currDict=currCT, prevDict=prevCT).to_csv(
    f"{CT_DELTA_FILE_ROOT}.csv"
)

combined_model = ModelClassDict(
    umlDict=currXMI,
    ctDict=currCT,
    apiDict=currAPI,
)

DataStructureReport(combDict=combined_model).write()

DataDictionaryReport(combDict=combined_model).write()

AlignmentReport(combDict=combined_model).write()
