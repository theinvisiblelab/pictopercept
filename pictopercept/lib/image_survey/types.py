from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from numpy import random

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
