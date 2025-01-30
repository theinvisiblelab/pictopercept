from typing import Dict
import logging

from pictopercept.lib.common_types import BaseSurvey
from pictopercept.surveys.occupations import OccupationsSurvey

loaded_surveys : Dict[str, BaseSurvey] = {}

# Loads all surveys from the file 'surveys.json' into memory.
# If there is an issue with any survey, it will exit the program.
def load_surveys():
    global loaded_surveys
    loaded_surveys = {
        "occupations": OccupationsSurvey(),
    }

    logging.getLogger(__name__).warning("[INFO] Surveys are OK.")
    if len(loaded_surveys) == 0:
        logging.getLogger(__name__).warning("[WARNING] There were 0 surveys loaded.")

def get_surveys() -> Dict[str, BaseSurvey]:
    global loaded_surveys
    return loaded_surveys

# Returns the survey by identifier, or None if not found
# Assumes loaded_surveys is not None, as if the loading
# of surveys fail, the program exits
def get_survey(identifier) -> BaseSurvey | None:
    global loaded_surveys
    if identifier in loaded_surveys: # and loaded_surveys[identifier].enabled:
        return loaded_surveys[identifier]

    return None
