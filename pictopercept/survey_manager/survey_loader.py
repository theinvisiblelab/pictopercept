from typing import Dict
import logging

from pictopercept.survey_manager import common_types
from pictopercept.survey_manager.implemented_surveys import jobs

loaded_surveys : Dict[str, common_types.BaseSurvey] = {}

# Loads all surveys from the file 'surveys.json' into memory.
# If there is an issue with any survey, it will exit the program.
def load_surveys():
    global loaded_surveys
    loaded_surveys = {
        "jobs": jobs.JobsSurvey(),
    }

    logging.getLogger(__name__).warning("[INFO] Surveys are OK.")
    if len(loaded_surveys) == 0:
        logging.getLogger(__name__).warning("[WARNING] There were 0 surveys loaded.")

def get_surveys() -> Dict[str, common_types.BaseSurvey]:
    global loaded_surveys
    return loaded_surveys

# Returns the survey by identifier, or None if not found
# Assumes loaded_surveys is not None, as if the loading
# of surveys fail, the program exits
def get_survey(identifier) -> common_types.BaseSurvey | None:
    global loaded_surveys
    if identifier in loaded_surveys: # and loaded_surveys[identifier].enabled:
        return loaded_surveys[identifier]

    return None
