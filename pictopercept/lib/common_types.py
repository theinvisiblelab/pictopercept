from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from pictopercept.lib.regular_question_survey.types import RegularQuestion
from pictopercept.lib.image_survey.types import AnswerTimer, PairQuestion

@dataclass
class GeneratedImageSurvey:
    pair_questions: List[PairQuestion]
    time_bar_duration: Optional[int]
    duration_seconds: Optional[int]
    dataset_folder_name: str
    accent_color: str

@dataclass
class GeneratedRegularSurvey:
    questions: List[RegularQuestion]


class BaseSurvey(metaclass=ABCMeta):
    # Mandatory properties of each Survey
    @property
    @abstractmethod
    def identifier(self) -> str: pass

    @property
    @abstractmethod
    def big_description(self) -> str: pass

    @property
    @abstractmethod
    def accent_color(self) -> str: pass

    @property
    @abstractmethod
    def answer_timer(self) -> AnswerTimer: pass

    @property
    @abstractmethod
    def duration_seconds(self) -> Optional[int]: pass

    @property
    @abstractmethod
    def dataset_folder_name(self) -> str: pass

    @property
    @abstractmethod
    def regular_questions(self) -> List[RegularQuestion]: pass


    # Mandatory methods of each Survey
    @abstractmethod
    def generate_image_survey(self) -> GeneratedImageSurvey: pass

    @abstractmethod
    def generate_regular_survey(self) -> GeneratedRegularSurvey: pass
