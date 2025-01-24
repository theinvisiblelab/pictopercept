from dataclasses import asdict
import json
import logging
from typing import Tuple

from flask import Request, Response, make_response, render_template, session
from pydantic import BaseModel, Field

from pictopercept.db import db_save_image_survey
from pictopercept.survey_manager import common_types

def get_handler(survey: common_types.BaseSurvey, current_step: str):
    generated_survey = survey.generate_image_survey()
    
    session["generated_survey"] = generated_survey;
    
    return render_template("survey.html", **{
        "generated_survey": generated_survey, # Used by our Python template
        "generated_survey_json": json.dumps(asdict(generated_survey)), # Used by JavaScript. TODO: Remove/drop the "attention_checks" field
        "survey_post_url": f"/survey/{survey.identifier}/{current_step}", # Used by JavaScript
    })

def post_handler(request: Request, survey: common_types.BaseSurvey) -> Response | None:
    # Answer class gotten from Frontend-POST
    class Answer(BaseModel):
        class Image(BaseModel):
            image: str = Field()
            chosen: bool = Field()

        images: Tuple[Image, Image] = Field()

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
                    ]
                })
            else:
                raise Exception("The answers provided do not match with the user-specific ones.")

        # Now, check for attention checks
        failed_attention_checks = 0
        for i, j in generated_survey["attention_checks"]:
            if i > len(clean_answers) or j > len(clean_answers):
                continue

            pair_0 = clean_answers[i]
            pair_1 = clean_answers[j]

            chosen_same = pair_0["images"][0]["chosen"] == pair_1["images"][1]["chosen"]

            if not chosen_same:
                failed_attention_checks += 1

        # Attention check fail threshold?
        # Should failed be stored also (they could be flagged)?
        logging.getLogger(__name__).warning(f"[INFO] Failed attention checks: {failed_attention_checks}")

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
