from ddf_ra_tools.parsers.xmi_parser import XMIParser
from ddf_ra_tools.parsers.api_parser import APIParser
from ddf_ra_tools.parsers.ct_parser import CTParser

from ddf_ra_tools.model.model_class import ModelClassDict

from ddf_ra_tools.reports.data_structure import DataStructureReport
from ddf_ra_tools.reports.data_dictionary import DataDictionaryReport
from ddf_ra_tools.reports.alignment import AlignmentReport
from ddf_ra_tools.reports.delta import DeltaReport

currCT = CTParser(
    "C:\\CDISC\\DDF-RA\\Deliverables\\CT\\USDM_CT.xlsx", version="3.11.1"
).get_model()
prevCT = CTParser(
    "C:\\CDISC\\DDF-RA-3.0.0\\Deliverables\\CT\\USDM_CT.xlsx", version="3.0.0"
).get_model()

deltaCT = DeltaReport(currDict=currCT, prevDict=prevCT)
deltaCT.to_csv("C:\\CDISC\\DDF-RA-Tools-Dev\\CT_DELTA.csv")
deltaCT.to_yaml("C:\\CDISC\\DDF-RA-Tools-Dev\\CT_DELTA.yml")

currAPI = APIParser(
    "C:\\CDISC\\DDF-RA\\Deliverables\\API\\USDM_API.json"
).get_model()
prevAPI = APIParser(
    "C:\\CDISC\\DDF-RA-3.0.0\\Deliverables\\API\\USDM_API.json"
).get_model()

deltaAPI = DeltaReport(currDict=currAPI, prevDict=prevAPI)
deltaAPI.to_csv("C:\\CDISC\\DDF-RA-Tools-Dev\\API_DELTA.csv")
deltaAPI.to_yaml("C:\\CDISC\\DDF-RA-Tools-Dev\\API_DELTA.yml")

currXMI = XMIParser(
    "C:\\CDISC\\DDF-RA\\Deliverables\\UML\\USDM_UML.xmi"
).get_model()
prevXMI = XMIParser(
    "C:\\CDISC\\DDF-RA-3.0.0\\Deliverables\\UML\\USDM_UML.xmi"
).get_model()

deltaUML = DeltaReport(currDict=currXMI, prevDict=prevXMI)
deltaUML.to_csv("C:\\CDISC\\DDF-RA-Tools-Dev\\UML_DELTA.csv")
deltaUML.to_yaml("C:\\CDISC\\DDF-RA-Tools-Dev\\UML_DELTA.yml")

combined_model = ModelClassDict(
    umlDict=currXMI,
    ctDict=currCT,
    apiDict=currAPI,
)

DataStructureReport(combDict=combined_model).to_yaml(
    ymlFile="C:\\CDISC\\DDF-RA-Tools-Dev\\dataStucture.yml"
)

DataDictionaryReport(combDict=combined_model).to_md(
    mdFile="C:\\CDISC\\DDF-RA-Tools-Dev\\dataDictionary.MD"
)

AlignmentReport(combDict=combined_model).to_csv(
    csvFile="C:\\CDISC\\DDF-RA-Tools-Dev\\alignment.csv"
)
