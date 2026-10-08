#!/usr/bin/env python3

#
#  Pipeline Manager Tool
#

import datetime
import json
import logging
import os
import sys
from os import path

import flywheel
from fw_client import FWClient

###############################################################################
# Logging Setup
###############################################################################

logger = logging.getLogger("fw_uploader")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

###############################################################################
# Flywheel Connector
###############################################################################

class FlywheelConnector:

    def __init__(self, api_key: str):
        self.APIKey: str = api_key
        self.project = None

        self.RestClient: FWClient = FWClient(api_key=self.APIKey)
        self.SDKClient = flywheel.Client(self.APIKey)

    def setProject(self, project_name: str) -> None:
        try:
            project_list = self.RestClient.get("/api/projects")
        except Exception as e:
            logger.error(f"Error retrieving project list: {e}")
            raise

        for p in project_list:
            if p.label.startswith(project_name):
                try:
                    self.project = self.SDKClient.get_project(p._id)  # noqa: SLF001
                except Exception as e:
                    logger.error(f"Cannot fetch project '{project_name}' via SDK: {e}")
                    raise
                logger.info(f"Project set: {self.project.label}")
                return

    def setProjectById(self, project_id: str) -> None:
            try:
                self.project = self.SDKClient.get_project(project_id)  # noqa: SLF001
            except Exception as e:
                logger.error(f"Cannot fetch project '{project_id}' via SDK: {e}")
                raise
            logger.info(f"Project set: {self.project.label}")

    def setProjectByObject(self, project) -> None:
            self.project = self.SDKClient.get_project(project)

###############################################################################
# Configuration
###############################################################################

class Config:

    def __init__(self, fileSpec: str):
        try:
            with open(fileSpec) as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Error reading config file '{fileSpec}': {e}")
            raise

    def get(self, target: str):
        return self.config.get(target)

###############################################################################
# Analysis Results
###############################################################################

class AnalysisResults:
    def __init__(self, fc):
        
        self.acquisition_analysis_results = {}

        #analyses = fc.SDKClient.get_analyses(project_id=fc.project.id)

        analyses_list = fc.RestClient.get(f"/api/projects/{fc.project._id}/all/analyses")
        # Project-level analyses
        for analysis in  analyses_list:
            #pprint.pprint (analysis)
            #input()
            if analysis.parents.subject != None:
                subject = fc.RestClient.get(f"/api/subjects/{analysis.parents.subject}")
                subject_label = subject.label
            else:
                subject_label = "None"
            if analysis.parents.session != None:
                session = fc.RestClient.get(f"/api/sessions/{analysis.parents.session}")
                session_label = session.label
            else:
                session_label = "None"
            if analysis.parents.acquisition != None:
                acquisition = fc.RestClient.get(f"/api/acquisitions/{analysis.parents.acquisition}")
                acquisition_label = acquisition.label
            else:
                acquisition_label = "None"
            job = fc.RestClient.get(f"/api/jobs/{analysis.job}")
            #logger.info(f"Analysis: {analysis.label}")

            try: 
                finished = job['transitions']['complete']
            except:
                finished = None

            acqKey = subject_label+session_label+acquisition_label
            if (acqKey in self.acquisition_analysis_results):
                if self.acquisition_analysis_results[acqKey] == None:
                    self.acquisition_analysis_results[acqKey] = finished
            else :
                self.acquisition_analysis_results[acqKey] = finished

            '''    
            analyses[analysis['label']] = {
                    "subject": subject_label,
                    "session": session_label,
                    "session_id": analysis.parents.session,
                    "acquisition_label": acquisition_label,
                    "acquisition_id": analysis.parents.acquisition,
                    "analysis_label": analysis.label,
                    "gear_name": analysis.gear_info.name,
                    "gear_version": analysis.gear_info.version,
                    "state": job.state,
                    "finished": finished
                }
            '''

###############################################################################
# Gear_tool
###############################################################################

class Gear_tool:
    def __init__(self, fc, label):
        self.fc = fc
        self.label = label
        self.qsm_inputs = ["input_file", "input_file_opt", "input_file_opt2"]
        self.qsm_input_index = 0
        self.inputs = {}
        self.inputs_names = []
        self.config = {}
        self.destination = {}
        self.destination_name = ""
        self.gear_name = "qsmxt"
        self.gear_type = "analysis"
        self.job_id = ""
        self.gear = self.fc.SDKClient.lookup(f'gears/{self.gear_name}')
        self.analysis_stastus = None

    def addQSM_input(self, file_info):
        self.inputs[self.qsm_inputs[self.qsm_input_index]] = file_info["file"]
        self.inputs_names.append(file_info['file_name'])
        self.qsm_input_index += 1
        self.destination = self.fc.SDKClient.get(file_info["acquisition_id"])
        self.destination_name = file_info['acquisition']

    def addAnatomical(self, file_info):
        self.inputs["anatomical"] = file_info["file"]
        self.inputs_names.append(file_info['file_name'])

    def addConfig(self, tag, value):
        self.config[tag] = value

    def print_gear_run(self):
        print ("gear:", self.gear_name)
        print ("inputs:", self.inputs)
        print ("config:", self.config)
        print ("destination:", self.destination)

    def set_analysis_status(self, status):
        self.analysis_status = status

    def run(self):
        dt = datetime.datetime.now()
        analysis_label = f"{self.gear_name} " + dt.strftime("%m/%d/%Y, %H:%M:%S")
        logger.info (f"{self.label}, {analysis_label}, {self.gear_name}, {self.inputs_names}, {self.config}, {self.destination_name}")
        self.job_id = self.gear.run(analysis_label=analysis_label, inputs=self.inputs, config=self.config, destination=self.destination)
        logger.info (f"job_id: {self.job_id}")

###############################################################################
# QSMxT_gear_tool
###############################################################################
class QSMxT_gear_tool(Gear_tool):
    def __init__(self, fc, label):
        self.gear_name = "qsmxt"
        super().__init__(fc, label)

###############################################################################
# Acquisition Classification and Launch
###############################################################################

class AcquisitionClassification:
    def __init__(self, fc, config):
        self.fc = fc
        self.do_reprocess = config.get("reprocess_all")
        self.do_qsmxt = config.get("do_qsmxt")
        self.do_qsm_medi = config.get("do_qsm_medi")

        self.sessions_dict = {}
    	
        for subject in fc.project.subjects.iter():
            for session in subject.sessions.iter():
                logger.info(f"Session: {subject.label}, {session.label}")
                sessionKey = subject.label+session.label
                self.sessions_dict[sessionKey] = {}
                acqs = {}
                for acquisition in session.acquisitions.iter():
                    acqKey = subject.label+session.label+acquisition.label
                    acqs[acqKey] = []
                    #print (acquisition.label)
                    for file in acquisition.files:

                        features = self.getClassification(file.classification, 'Features')
                        intent =  self.getClassification(file.classification, 'Intent')
                        measurement = self.getClassification(file.classification, 'Measurement')
                        scanOrientation = self.getClassification(file.classification, 'Scan Orientation')

                        acqs[acqKey].append({
                            "group": fc.project.group,
                            "project": fc.project.label,
                            "subject": subject.label,
                            "session": session.label,
                            "session_id": session._id,
                            "acquisition": acquisition.label,
                            "acquisition_id": acquisition._id,
                            "file": file,
                            "file_name": file.name,
                            "file_id": file.id,
                            "modality": file.modality,
                            "file_type": file.type,
                            "features": features,
                            "Intent": intent,
                            "Measurement": measurement,
                            "Scan Orientation": scanOrientation
                        })
                self.sessions_dict[sessionKey] = acqs

    def launchGears(self, analyses):
        for i in self.sessions_dict.keys():
            gearList = []
            for sacqs in self.sessions_dict[i]:
                structImage = None
                aGear = QSMxT_gear_tool(self.fc, sacqs)
                gearList.append(aGear)
                if sacqs in analyses.acquisition_analysis_results.keys():
                    aGear.set_analysis_status(analyses.acquisition_analysis_results[sacqs])
                else:
                    aGear.set_analysis_status(None)
                for f in self.sessions_dict[i][sacqs]:
                    try:
                        if f["Intent"][0] == "QSM":
                            aGear.addQSM_input(f)
                        if f["Intent"][0] == "Structural":
                            structImage = f
                    except:
                        logger.info(f"Cannot read classification info. ({sacqs})")
            for g in gearList:
                if g.destination:
                    #print (f"Gear Status {g.destination_name}, {g.analysis_status}")
                    if structImage:
                        g.addAnatomical(structImage)
                        g.addConfig('premade', 'bet')
                    if g.analysis_status == None:
                        g.run()

    def getClassification(self, classification, target):

        try:
            value = classification[target]
        except:
            value = None

        return value



###############################################################################
# Main
###############################################################################


def main() -> None:
    context = flywheel.GearContext()

    config_opts = context.config.opts


    analysis = context.client.get_analysis(context.destination["id"])

    project_id = analysis.parent["id"]
    project = context.client.get_project(project_id)


    logger.info(f"project: {project.label}")

    project_name = project.label

    api_key_input = context.get_input('api-key')
    api_key = api_key_input['key'] if api_key_input else None

    if not api_key:
        raise ValueError(
            "FLYWHEEL_API_KEY environment variable or config APIKey required"
        )

    if not api_key :
        logger.error("Missing APIKey or project in config file.")
        sys.exit(1)

    #try:
    fc = FlywheelConnector(api_key)
    fc.setProject(project_name)
    #fc.setProjectByObject(project)
    
    
    AR = AnalysisResults(fc)
    AC = AcquisitionClassification(fc, config_opts)
    AC.launchGears(AR)
    
    #except Exception as e:
    #    logger.error(f"Fatal error: {e}")
    #    sys.exit(1)


if __name__ == "__main__":
    main()
