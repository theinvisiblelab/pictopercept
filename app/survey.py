from typing import Dict, List
from django.conf import settings
import pandas as pd
import json
import logging

BASE_DIR = settings.BASE_DIR

class AnswerTimer:
    mode: str
    seconds: int

    def __init__(self, data):
        try:
            self.mode = str(data["mode"])
            if self.mode not in ["on", "off", "random"]:
                raise ValueError(f'Mode must be "on", "off", or "random".')

            if self.mode != "off":
                self.seconds = int(data["seconds"])
        except Exception as e:
            raise ValueError(f'Missing {e} field.')

class Question:
    format: str
    variables: Dict[str, List[str]]

    def __init__(self, data):
        try:
            if not isinstance(data["variables"], Dict):
                raise ValueError("Variables must be a map.")
            else:
                for variable_key, variable_values in data["variables"].items():
                    if not isinstance(variable_key, str) or not all(isinstance(value, str) for value in variable_values):
                        raise ValueError("Variables must be a map of key string and value list of strings.")

            self.format = str(data["format"])
            self.variables = data["variables"]
        except Exception as e:
            raise ValueError(f'Invalid Question format: {e}')

    def as_json(self):
        return {
            "format": self.format,
            "variables": self.variables,
        }

class Survey:
    identifier: str
    enabled: bool
    big_description: str
    datasets: List[str]
    question: Question
    image_server: str
    duration_seconds: int | None
    sustantive: str
    db_collection: str
    answer_timer: AnswerTimer | None

    def __init__(self, data):
        # Critical/mandatory variables
        try:
            self.identifier = str(data["identifier"])
            self.big_description = str(data["big-description"])
            self.image_server = str(data["image-server"])
            self.db_collection = str(data["db-collection"])
            self.sustantive = str(data["sustantive"])

            if isinstance(data["enabled"], bool):
                self.enabled = data["enabled"]
            else:
                raise ValueError(f'"enabled" must be a string.')


            if isinstance(data["datasets"], List):
                self.datasets = [str(dataset) for dataset in data["datasets"]]
            else:
                raise ValueError(f'"datasets" must be a string or a list of strings.')

            self.question = Question(data["question"])
        except KeyError as e:
            raise ValueError(f'Missing mandatory field {e}. Check Survey JSON fields doc.')

        # Optional variables
        self.duration_seconds = data.get("duration-seconds", None)

        if "answer-timer" in data:
            try:
                self.answer_timer = AnswerTimer(data["answer-timer"])
            except Exception as e:
                raise ValueError(f'Invalid "answer-timer" format: {e}')
        else:
            self.answer_timer = None

    def load_datasets(self):
        df = pd.concat((pd.read_csv(f'./app/datasets/{dataset}') for dataset in self.datasets), ignore_index=True)
        df = df[~df['age'].isin(['0-2', '3-9', '10-19'])]  # drop non-adults
        df = df.sample(frac=1).reset_index(drop=True)  # shuffle rows
        return df
    
    def use_timer_bar(self):
        from numpy import random
        if self.answer_timer is not None:
            if self.answer_timer.mode == "on":
                return True
            elif self.answer_timer.mode == "random":
                return random.choice([True, False])

        return False # If None or mode is "off"

def load_surveys():
    surveys = []

    try:
        with open(BASE_DIR / "./app/surveys.json") as f:
            survey_datas = json.loads(f.read())
            survey_idx = 0
            for survey_data in survey_datas:
                try:
                    surveys.append(Survey(survey_data))
                except Exception as e:
                    logging.getLogger(__name__).warning(f'[WARNING] The survey with index {survey_idx} was not loaded. Error: {e}')
                survey_idx += 1
    except Exception as e:
        logging.getLogger(__name__).error(f'[ERROR] Could not open the surveys file: {e}')

    return surveys

def load_survey(identifier) -> Survey|None:
    surveys = load_surveys()
    for survey in surveys:
        if survey.identifier == identifier:
            if not survey.enabled:
                return None
            return survey

    return None
