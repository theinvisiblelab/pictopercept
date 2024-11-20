from pydantic import BaseModel, Field
from typing import Dict, List
from enum import Enum
import pandas as pd
import logging
import json

class AnswerTimerModeEnum(str, Enum):
    on = 'on'
    off = 'off'
    random = 'random'

class AnswerTimer(BaseModel):
    mode: AnswerTimerModeEnum = Field()
    seconds: int = Field()

class Question(BaseModel):
    format: str
    variables: Dict[str, List[str]]


class Survey(BaseModel):
    identifier: str = Field()
    db_collection: str = Field()
    enabled: bool  = Field()

    sustantive: str = Field()
    big_description: str = Field()

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


def load_surveys() -> Dict[str, Survey]:
    surveys = {}

    try:
        with open("./pictopercept/surveys.json") as f:
            survey_datas = json.loads(f.read())
            survey_idx = 0
            for survey_data in survey_datas:
                try:
                    survey = Survey(**survey_data)
                    surveys[survey.identifier] = survey
                except Exception as e:
                    logging.getLogger(__name__).critical(f'[ERROR] The survey with index {survey_idx} has an error. Error: {e}')
                    exit(0)
                survey_idx += 1
    except Exception as e:
        logging.getLogger(__name__).critical(f'[ERROR] Could not open the surveys file: {e}')
        exit(0)

    return surveys

def load_survey(identifier) -> Survey | None:
    surveys = load_surveys()
    if identifier in surveys and surveys[identifier].enabled:
        return surveys[identifier]

    return None
