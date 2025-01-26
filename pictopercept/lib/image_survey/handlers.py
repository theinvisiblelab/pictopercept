from dataclasses import asdict
import json
import logging
from typing import Tuple

from flask import Request, Response, make_response, render_template, session
from pydantic import BaseModel, Field

from pictopercept.db import db_save_image_survey
from pictopercept.lib.common_types import BaseSurvey

def get_handler(survey: BaseSurvey, current_step: str):
    generated_survey = survey.generate_image_survey()
    
    session["generated_survey"] = generated_survey;

    generated_survey_json = asdict(generated_survey)
    generated_survey_json.pop("dataset_folder_name")
    
    return render_template("survey.html", **{
        "generated_survey": generated_survey, # Used by our Python template
        "generated_survey_json": json.dumps(generated_survey_json), # Used by JavaScript.
        "survey_post_url": f"/survey/{survey.identifier}/{current_step}", # Used by JavaScript
    })

def post_handler(request: Request, survey: BaseSurvey) -> Response | None:
    # Answer class gotten from Frontend-POST
    class Answer(BaseModel):
        class Image(BaseModel):
            image: str = Field()
            chosen: bool = Field()

        images: Tuple[Image, Image] = Field()
        seconds_taken: float = Field()

    try:
        # Each answer is a pair containing both
        # options to choose from
        try:
            answers = request.get_json()
        except:
            # Custom error message when invalid json
            raise Exception("The request does not have a proper body.")

        # This is safe to use, as is injected and encrypted into the session cookie.
        generated_survey = session["generated_survey"]
        user_id : str = session["user_id"]

        clean_answers = []
        for pair_question, answer in zip(generated_survey["pair_questions"], answers):
            try:
                clean_answer = Answer(**answer)
            except Exception:
                raise Exception("The answer format is wrong.") # Raise custom exception, instead of Pydantic one

            image_0 = clean_answer.images[0]
            image_1 = clean_answer.images[1]

            valid_images = image_0.image == pair_question["images"][0] and image_1.image == pair_question["images"][1]
            valid_choice = (image_0.chosen and not image_1.chosen) or (image_1.chosen and not image_0.chosen)

            if valid_images and valid_choice:
                clean_answers.append({
                    "userId": user_id,
                    "images": [
                        {
                            "image": image_0.image,
                            "chosen": image_0.chosen,
                        },
                        {
                            "image": image_1.image,
                            "chosen": image_1.chosen,
                        },
                    ],
                    "secondsTaken": clean_answer.seconds_taken
                })
            else:
                raise Exception("The answers provided do not match with the user-specific ones.")

        try:
           db_save_image_survey(clean_answers, session["survey_db_collection"])
        except Exception as e:
            logging.getLogger(__name__).error("[ERROR] Error saving user answers into the MongoDB database.")
            logging.getLogger(__name__).error("[ERROR] " + str(e))
            return make_response(f"There was an error with the database while saving your answers.", 500)
        else:
            return None
    except Exception as e:
            return make_response(f"Error validating the answers: '{str(e)}'", 400)
