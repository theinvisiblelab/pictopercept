from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import os
from typing import List, Optional

from pictopercept.lib.regular_question_survey.types import RegularQuestion
from pictopercept.lib.image_survey.types import AnswerTimer, PairQuestion

MAX_USER_ID_LEN = 36 # ProlificID's len is 24, and uuid4's 36 
DATASETS_PATH = os.environ.get("DATASETS_PATH", "/data/datasets")

@dataclass
class GeneratedImageSurvey:
    pair_questions: List[PairQuestion]
    time_bar_duration: Optional[int]
    duration_seconds: Optional[int]
    image_dataset_path: str
    accent_color: str
    identifier: str

@dataclass
class GeneratedRegularSurvey:
    questions: List[RegularQuestion]

@dataclass
class SurveyMetadata():
    identifier: str
    big_description: str
    accent_color: str
    answer_timer: AnswerTimer
    duration_seconds: Optional[int]
    image_dataset_path: str
    regular_questions: List[RegularQuestion]
    regular_questions_enabled: bool

class BaseSurvey(metaclass=ABCMeta):
    @property
    @abstractmethod
    def metadata(self) -> SurveyMetadata: pass

    # Mandatory methods of each Survey
    @abstractmethod
    def generate_image_survey(self) -> GeneratedImageSurvey: pass

    @abstractmethod
    def generate_regular_survey(self) -> GeneratedRegularSurvey: pass
