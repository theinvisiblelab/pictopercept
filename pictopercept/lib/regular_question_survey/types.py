from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


class RegularQuestion(metaclass=ABCMeta):
    @property
    @abstractmethod
    def kind(self) -> str: pass

    @abstractmethod
    def validate(self, answer) -> Dict | str: pass

@dataclass
class MultipleChoice(RegularQuestion):
    @property
    def kind(self) -> str:
        return "MultipleChoice"

    title: str
    other_enabled: bool
    options: List[str]
    min_other_len :int = 3
    max_other_len :int = 20

    def validate(self, answer) -> Dict | str:
        if len(answer["checkedAnswers"]) == 0 and answer["otherAnswer"] is None:
            return "You must check at least one option."

        clean_answer = {
            "checked_answers": [],
            "other_answer": None,
        }

        for chosen_index in answer["checkedAnswers"]:
            if int(chosen_index) < 0 or int(chosen_index) >= len(self.options):
                raise Exception("")
            clean_answer["checked_answers"].append(self.options[chosen_index])

        if answer["otherAnswer"] is not None:
            answer_text = answer["otherAnswer"].strip()
            answer_len = len(answer_text)

            if answer_len == 0:
                return "You must fill the \"other\" text field if you selected it."
            elif answer_len < self.min_other_len or answer_len > self.max_other_len:
                return f"Your \"other\" answer must be between {self.min_other_len}-{self.max_other_len} characters length."
            else:
                clean_answer["other_answer"] = answer["otherAnswer"]

        return clean_answer

@dataclass
class SingleChoice(RegularQuestion):
    @property
    def kind(self) -> str:
        return "SingleChoice"

    title: str
    other_enabled: bool
    options: List[str]

    def validate(self, answer) -> Dict | str:
        if answer["checkedAnswer"] is None and answer["otherAnswer"] is None:
            return "You must check one option."

        if answer["checkedAnswer"] is not None:
            chosen_index = answer["checkedAnswer"]
            if int(chosen_index) < 0 or int(chosen_index) >= len(self.options):
                raise Exception("")

            return {
                "checked_answer": self.options[chosen_index],
                "other_answer": None,
            }
        else:
            if len(answer["otherAnswer"].strip()) == 0:
                return "You must fill the \"other\" text field if you selected it."
            elif len(answer["otherAnswer"].strip()) < 3 or len(answer["otherAnswer"].strip()) > 20:
                return "Your \"other\" answer must be between 3-20 characters length."
            else:
                return {
                    "checked_answer": None,
                    "other_answer": answer["otherAnswer"]
                }

@dataclass
class Matrix(RegularQuestion):
    @property
    def kind(self) -> str:
        return "Matrix"

    title: str
    options: List[str]

    def validate(self, answer) -> Dict | str:
        if len(answer["checkedAnswers"]) == 0:
            return "You must answer all rows."
        
        clean_answer = {
            "checked_answers": []
        }
        
        # 5 options in total, covering [0, 4]
        MATRIX_MIN = 0
        MATRIX_MAX = 4
        
        for chosen_index in answer["checkedAnswers"]:
            if int(chosen_index) < MATRIX_MIN or int(chosen_index) > MATRIX_MAX:
                raise Exception("")
            clean_answer["checked_answers"].append(int(chosen_index))

        return clean_answer

@dataclass
class AgreementScale(RegularQuestion):
    @property
    def kind(self) -> str:
        return "AgreementScale"

    title: str

    def validate(self, answer) -> Dict | str:
        if answer["checkedAnswer"] is None:
            return "You must choose one option."
        
        # 5 options in total, covering [0, 4]
        AGREEMENT_MIN = 0
        AGREEMENT_MAX = 4
        
        chosen_index = answer["checkedAnswer"]
        
        if int(chosen_index) < AGREEMENT_MIN or int(chosen_index) > AGREEMENT_MAX:
            raise Exception("")
        
        return {
            "checked_answer": self.agreement_value_as_string(chosen_index)
        }

    def agreement_value_as_string(self, value : int):
        match value:
            case 0:
                return "Strongly disagree"
            case 1:
                return "Disagree"
            case 2:
                return "Neutral"
            case 3:
                return "Agree"
            case 4:
                return "Strongly agree"
        return "Unknown value"

@dataclass
class OpenShort(RegularQuestion):
    @property
    def kind(self) -> str:
        return "OpenShort"

    title: str
    min_len: int
    max_len: int

    def validate(self, answer) -> Dict | str:
        answer_text = answer["answerText"].strip()
        answer_len = len(answer_text)
        if answer_len == 0:
            return "You must answer this question."
        elif answer_len < self.min_len or answer_len > self.max_len:
            return f"Your answer must be between {self.min_len}-{self.max_len} characters length."
        
        clean_answer = {
            "answer_text" : answer_text
        }
        return clean_answer
