import logging
import os
from typing import List, Optional, final

import numpy as np
import pandas as pd

from pictopercept.survey_manager import common_types
from pictopercept.survey_manager import regular_question_types

@final
class JobsSurvey(common_types.BaseSurvey):
    @property
    def identifier(self) -> str:
        return "jobs"

    @property
    def big_description(self) -> str:
        return "<p>Welcome to the PictoPercept survey! You'll see pairs of photos and a job title, like \"Who of these is a teacher?\" or \"Who of these is a painter?\" Pick the person you think fits the job more by clicking the button.</p><p>Trust your instincts!</p>"

    @property
    def accent_color(self) -> str:
        return "#ff4b4b"

    @property
    def answer_timer(self) -> common_types.AnswerTimer:
        return common_types.AnswerTimer(common_types.AnswerTimerMode.random, 6)

    @property
    def duration_seconds(self) -> Optional[int]:
        return 5

    @property
    def dataset_path(self) -> str:
        return os.environ.get("CFD_DATASET_PATH", "")

    @property
    def regular_questions(self) -> List[regular_question_types.RegularQuestion]:
        return [
            regular_question_types.MultipleChoice("Which of the following best describes your primary occupational status?", True, [
                "Employed (full-time)",
                "Employed (part-time)",
                "Self-employed",
                "Unemployed",
                "Retired",
                "Student"
            ]),
            regular_question_types.Matrix("How familiar are you with each of the following occupations based on personal experience or people you know? (1 = Not at all familiar; 5 = Extremely familiar)", [
                "Teacher",
                "Doctor",
                "Plumber"
            ]),
            regular_question_types.MultipleChoice("How often do you consume TV shows, movies, social media, or news that depict various occupations (e.g., in dramas, documentaries, social media content)?", False, [
                "Never",
                "Rarely (less than once a week)",
                "Sometimes (1-3 times a week)",
                "Often (4-6 times a week)",
                "Very often (daily)"
            ]),
            regular_question_types.AgreementScale("Media portrayals generally provide realistic depictions of different occupations."),
            regular_question_types.AgreementScale("I notice stereotypes about certain jobs when I watch TV shows or movies."),
            regular_question_types.AgreementScale("It is easy to guess someone’s occupation just by looking at them."),
            regular_question_types.AgreementScale("I believe stereotypes about occupations exist for a reason (i.e., there is some truth to them)."),
            regular_question_types.AgreementScale("Even if I notice stereotypes, I try not to let them influence my judgment."),
            regular_question_types.AgreementScale("When answering surveys, I try to provide responses that I believe are more socially acceptable, even if they don’t perfectly reflect my true feelings."),
            regular_question_types.MultipleChoice("In my workplace or daily social environment, I frequently interact with people from diverse backgrounds (e.g., different races, genders, or cultures).", False, [
                "Different races",
                "Different genders",
                "Different cultures"
            ]),
            regular_question_types.OpenShort("In your own words, how do you think stereotypes (or biases) about certain occupations develop in society?")
        ]

    cfd_dataset: pd.DataFrame

    def __init__(self):
        self.load_dataset("cfd.csv")

    def load_dataset(self, dataset: str):
        df = pd.read_csv("pictopercept/datasets/"+dataset)

        if not isinstance(df, pd.DataFrame):
            logging.getLogger(__name__).critical("[ERROR] There is no DataFrame dataset loaded. Is it instance of DataFrame?")
            exit(1)

        self.cfd_dataset = df

    def generate_question_text(self) -> List[str]:
        jobs = [
            "a Chief Executive Officer (CEO)",
            "a Computer Programmer",
            "a Doctor",
            "a Nurse",
            "a Primary School Teacher",
            "a Police Officer",
            "a Housekeeper",
            "a Construction Worker"
        ]

        generated_jobs = np.matrix([[job for _ in range(8)] for job in jobs])
        return generated_jobs.flatten().tolist()[0]


    def generate_image_survey(self) -> common_types.GeneratedImageSurvey:
        desired_pair_count = 64
        survey_images = self.cfd_dataset["file"].sample(desired_pair_count * 2).tolist()
        generated_jobs = self.generate_question_text()

        image_count = len(survey_images)

        # Create the pairs
        final_pairs = []
        for i, job in zip(range(0, image_count, 2), generated_jobs):
            question_text = f"Who of these is {job}?"
            final_pairs.append(common_types.PairQuestion((survey_images[i], survey_images[i+1]), question_text))

        # Select 6 random pairs as attention checks, flip them and add them
        repeated_pairs = np.random.choice(final_pairs, 6, replace=False)
        for rp in repeated_pairs:
            flipped_pair = (rp.images[1], rp.images[0])
            final_pairs.append(common_types.PairQuestion(flipped_pair, rp.text))

        np.random.shuffle(final_pairs)

        time_bar_duration = None
        if self.answer_timer.should_use():
            time_bar_duration = self.answer_timer.duration

        return common_types.GeneratedImageSurvey(final_pairs, time_bar_duration, self.duration_seconds, self.dataset_path, self.accent_color)
    
    def generate_regular_survey(self) -> common_types.GeneratedRegularSurvey:
        regular_questions = self.regular_questions
        return common_types.GeneratedRegularSurvey(regular_questions)
