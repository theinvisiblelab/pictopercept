from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from numpy import random

class AnswerTimerMode(Enum):
    never = 0
    always = 1
    random = 2

@dataclass
class AnswerTimer:
    mode: AnswerTimerMode
    duration: int

    def should_use(self) -> bool:
        match self.mode:
            case AnswerTimerMode.always:
                return True
            case AnswerTimerMode.never:
                return False
            case AnswerTimerMode.random:
                return random.choice([True, False])

@dataclass
class PairQuestion:
    images: Tuple[str, str]
    text: str
