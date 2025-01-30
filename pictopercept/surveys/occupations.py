import logging
import os
from typing import Dict, List, Tuple, final

import numpy as np
from numpy import random

from pictopercept.lib.common_types import BaseSurvey, GeneratedImageSurvey, GeneratedRegularSurvey, DATASETS_PATH, SurveyMetadata
from pictopercept.lib.image_survey.types import AnswerTimer, AnswerTimerMode, PairQuestion
from pictopercept.lib.regular_question_survey.types import AgreementScale, Matrix, MultipleChoice, OpenShort

@final
class OccupationsSurvey(BaseSurvey):
    @property
    def metadata(self) -> SurveyMetadata:
        return SurveyMetadata(
            identifier="occupations",
            image_dataset_path = f"{DATASETS_PATH}/chicago_face_dataset/",

            big_description = "<p>Welcome to the PictoPercept survey! You'll see pairs of photos and a job title, like \"Who of these is a teacher?\" or \"Who of these is a painter?\" Pick the person you think fits the job more by clicking the button.</p><p>Trust your instincts!</p>",
            accent_color = "#ff4b4b",

            answer_timer = AnswerTimer(AnswerTimerMode.random, 6),
            duration_seconds = 180,
            regular_questions_enabled = False,
            regular_questions = [
                MultipleChoice("Which of the following best describes your primary occupational status?", True, [
                    "Employed (full-time)",
                    "Employed (part-time)",
                    "Self-employed",
                    "Unemployed",
                    "Retired",
                    "Student"
                ]),
                Matrix("How familiar are you with each of the following occupations based on personal experience or people you know? (1 = Not at all familiar; 5 = Extremely familiar)", [
                    "Teacher",
                    "Doctor",
                    "Plumber"
                ]),
                MultipleChoice("How often do you consume TV shows, movies, social media, or news that depict various occupations (e.g., in dramas, documentaries, social media content)?", False, [
                    "Never",
                    "Rarely (less than once a week)",
                    "Sometimes (1-3 times a week)",
                    "Often (4-6 times a week)",
                    "Very often (daily)"
                ]),
                AgreementScale("Media portrayals generally provide realistic depictions of different occupations."),
                AgreementScale("I notice stereotypes about certain jobs when I watch TV shows or movies."),
                AgreementScale("It is easy to guess someone’s occupation just by looking at them."),
                AgreementScale("I believe stereotypes about occupations exist for a reason (i.e., there is some truth to them)."),
                AgreementScale("Even if I notice stereotypes, I try not to let them influence my judgment."),
                AgreementScale("When answering surveys, I try to provide responses that I believe are more socially acceptable, even if they don’t perfectly reflect my true feelings."),
                MultipleChoice("In my workplace or daily social environment, I frequently interact with people from diverse backgrounds (e.g., different races, genders, or cultures).", False, [
                    "Different races",
                    "Different genders",
                    "Different cultures"
                ]),
                OpenShort("In your own words, how do you think stereotypes (or biases) about certain occupations develop in society?", 8, 50)
            ]
        )

    cfd_image_groups: Dict[str, List[str]]
    cfd_category_pairs: List[Tuple[str, str]]

    def __init__(self):
        neutral_images = []
        
        logging.getLogger(__name__).warning(f"Dataset path: {self.metadata.image_dataset_path}")
        for file in os.listdir(self.metadata.image_dataset_path):
            if file.endswith(".jpg"):
                neutral_images.append(file)
        
        # should be 597 images
        logging.getLogger(__name__).warning(f"[INFO] Found {len(neutral_images)} neutral images for \"occupations\" survey.")

        self.cfd_image_groups = {f"{ethnicity}{gender}":[] for ethnicity in "ABWL" for gender in "MF"}
        for img in neutral_images:
            parts = img.split("-") # Example: CFD-BM-201-077-N.jpg → ['CFD', 'BM', '201', '077', 'N.jpg']
            ethnicity_gender = parts[1] # Extract ethnicity & gender (e.g., "BM", "AF", etc.)
            if ethnicity_gender in self.cfd_image_groups:
                self.cfd_image_groups[ethnicity_gender].append(img)

        # Generate all 64 possible pairs
        self.cfd_category_pairs =[(cat1, cat2) for cat1 in self.cfd_image_groups for cat2 in self.cfd_image_groups] 

    def generate_question_text(self) -> List[str]:
        occupations = [
            "a Chief Executive Officer (CEO)",
            "a Computer Programmer",
            "a Doctor",
            "a Nurse",
            "a Primary School Teacher",
            "a Police Officer",
            "a Housekeeper",
            "a Construction Worker"
        ]

        generated_occupations = np.matrix([[occupation for _ in range(8)] for occupation in occupations])
        return generated_occupations.flatten().tolist()[0]


    def generate_image_survey(self) -> GeneratedImageSurvey:
        # Randomly select an image from each category for the pairs
        image_pairs = []
        for cat1, cat2 in self.cfd_category_pairs:
            if self.cfd_image_groups[cat1] and self.cfd_image_groups[cat2]:  # Ensure there are images in both categories
                img1 = random.choice(self.cfd_image_groups[cat1])
                img2 = random.choice(self.cfd_image_groups[cat2])
                image_pairs.append((img1, img2))
        
        random.shuffle(image_pairs) # shuffle so images shown are not too predictable in order

        generated_occupations = self.generate_question_text()

        # Create the pairs
        final_pairs = []
        for image_pair, job in zip(image_pairs, generated_occupations):
            question_text = f"Who of these is {job}?"
            final_pairs.append(PairQuestion(image_pair, question_text))

        # Select 6 random pairs as attention checks, flip them and add them
        repeated_pairs = np.random.choice(final_pairs, 6, replace=False)
        for rp in repeated_pairs:
            flipped_pair = (rp.images[1], rp.images[0])
            final_pairs.append(PairQuestion(flipped_pair, rp.text))

        np.random.shuffle(final_pairs)

        time_bar_duration = None
        if self.metadata.answer_timer.should_use():
            time_bar_duration = self.metadata.answer_timer.duration

        return GeneratedImageSurvey(final_pairs, time_bar_duration, self.metadata.duration_seconds, self.metadata.image_dataset_path, self.metadata.accent_color, "occupations")
    
    def generate_regular_survey(self) -> GeneratedRegularSurvey:
        regular_questions = self.metadata.regular_questions
        return GeneratedRegularSurvey(regular_questions)
