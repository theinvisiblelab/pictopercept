from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from numpy import random

from pictopercept.survey_manager import regular_question_types


class AnswerTimerMode(Enum):
    on = 0
    off = 1
    random = 2

@dataclass
class AnswerTimer:
    mode: AnswerTimerMode
    duration: int

    def should_use(self) -> bool:
        match self.mode:
            case AnswerTimerMode.on:
                return True
            case AnswerTimerMode.off:
                return False
            case AnswerTimerMode.random:
                return random.choice([True, False])

@dataclass
class PairQuestion:
    images: Tuple[str, str]
    text: str

@dataclass
class GeneratedImageSurvey:
    pair_questions: List[PairQuestion]
    time_bar_duration: Optional[int]
    duration_seconds: Optional[int]
    image_url_prefix: str
    accent_color: str

@dataclass
class GeneratedRegularSurvey:
    questions: List[regular_question_types.RegularQuestion]


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
    def image_url_prefix(self) -> str: pass

    @property
    @abstractmethod
    def regular_questions(self) -> List[regular_question_types.RegularQuestion]: pass


    # Mandatory methods of each Survey
    @abstractmethod
    def generate_image_survey(self) -> GeneratedImageSurvey: pass

    @abstractmethod
    def generate_regular_survey(self) -> GeneratedRegularSurvey: pass
