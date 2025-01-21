import errno
from pydantic import BaseModel, Field
from typing import Dict, List
from enum import Enum
import pandas as pd
import logging
import json

class QuestionSurvey(BaseModel):
    pass

class ImageSurvey(BaseModel):
    pass

class Survey(BaseModel):
    class AnswerTimer(BaseModel):
        class AnswerTimerModeEnum(str, Enum):
            on = 'on'
            off = 'off'
            random = 'random'

        mode: AnswerTimerModeEnum = Field()
        seconds: int = Field()
    
    class Question(BaseModel):
        format: str
        variables: Dict[str, List[str]]

    identifier: str = Field()
    db_collection: str = Field()
    enabled: bool  = Field()

    big_description: str = Field()

    accent_color: str = Field(default="#ff4b4b")

    duration_seconds: int | None = Field(default=None)
    answer_timer: AnswerTimer | None = Field(default=None)

    question: Question = Field()

    datasets: List[str] = Field()
    image_server: str = Field()


    def load_datasets(self):
        df = pd.concat((pd.read_csv("pictopercept/datasets/"+dataset) for dataset in self.datasets), ignore_index=True)
        df = df[~df['age'].isin(['0-2', '3-9', '10-19'])]  # drop non-adults
        df = df.sample(frac=1).reset_index(drop=True)  # shuffle rows
        return df
    
    def use_timer_bar(self) -> bool:
        from numpy import random
        if self.answer_timer is not None:
            if self.answer_timer.mode == "on":
                return True
            elif self.answer_timer.mode == "random":
                return bool(random.choice([True, False]))

        return False # If None or mode is "off"


loaded_surveys = None

# Loads all surveys from the file 'surveys.json' into memory.
# If there is an issue with any survey, it will exit the program.
def load_surveys():
    global loaded_surveys
    surveys = {}

    try:
        with open("./pictopercept/surveys.json") as f:
            survey_datas = json.loads(f.read())
            survey_idx = 0
            for survey_data in survey_datas:
                try:
                    survey = Survey(**survey_data)
                    if survey.enabled:
                        surveys[survey.identifier] = survey
                except Exception as e:
                    logging.getLogger(__name__).critical(f'[ERROR] The survey with index {survey_idx} has an error. Error: {e}')
                    exit(errno.EINTR)
                survey_idx += 1
    except Exception as e:
        logging.getLogger(__name__).critical(f'[ERROR] Could not open the surveys file: {e}')
        exit(errno.EINTR)

    logging.getLogger(__name__).warning("[INFO] Surveys are OK.")
    if len(surveys) == 0:
        logging.getLogger(__name__).warning("[WARNING] There were 0 surveys loaded.")

    loaded_surveys = surveys

def get_surveys() -> dict[str, Survey]:
    global loaded_surveys
    return loaded_surveys

# Returns the survey by identifier, or None if not found
# Assumes loaded_surveys is not None, as if the loading
# of surveys fail, the program exits
def get_survey(identifier) -> Survey | None:
    global loaded_surveys
    if identifier in loaded_surveys and loaded_surveys[identifier].enabled:
        return loaded_surveys[identifier]

    return None
