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

    def validate(self, answer) -> Dict | str:
        if len(answer["checkedAnswers"]) == 0 and answer["otherAnswer"] is None:
            return "You must check at least one option."

        clean_answer = {
            "checked_answers": [],
            "other_answer": None,
        }

        for chosenIndex in answer["checkedAnswers"]:
            if int(chosenIndex) < 0 or int(chosenIndex) >= len(self.options):
                raise Exception("")
            clean_answer["checked_answers"].append(int(chosenIndex))

        if answer["otherAnswer"] is not None:
            if len(answer["otherAnswer"].strip()) == 0:
                return "You must fill the \"other\" text field if you selected it."
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
            chosenIndex = answer["checkedAnswer"]
            if int(chosenIndex) < 0 or int(chosenIndex) >= len(self.options):
                raise Exception("")

            return {
                "checked_answer": int(chosenIndex),
                "other_answer": None,
            }
        else:
            if len(answer["otherAnswer"].strip()) == 0:
                return "You must fill the \"other\" text field if you selected it."
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
        
        for chosenIndex in answer["checkedAnswers"]:
            if int(chosenIndex) < MATRIX_MIN or int(chosenIndex) > MATRIX_MAX:
                raise Exception("")
            clean_answer["checked_answers"].append(int(chosenIndex))

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
        
        chosenIndex = answer["checkedAnswer"]
        
        if int(chosenIndex) < AGREEMENT_MIN or int(chosenIndex) > AGREEMENT_MAX:
            raise Exception("")
        
        return {
            "checked_answer": int(chosenIndex)
        }

@dataclass
class OpenShort(RegularQuestion):
    @property
    def kind(self) -> str:
        return "OpenShort"

    title: str

    def validate(self, answer) -> Dict | str:
        answerText = answer["answerText"].strip()
        if len(answerText) == 0:
            return "You must answer this question."
        
        clean_answer = {
            "answer_text" : answerText
        }
        return clean_answer
