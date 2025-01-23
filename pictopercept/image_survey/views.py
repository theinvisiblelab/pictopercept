import logging
from typing import Dict, List

from flask import Request, Response, make_response, render_template, session
from pydantic import BaseModel, Field

from pictopercept.db import db_save_image_survey
from pictopercept.survey_loader import Survey

def get_handler(survey: Survey, current_step: str):
    df = survey.image_survey.load_datasets()
    
    image_urls = df[:200]["file"].tolist()
    time_bar_enabled = survey.image_survey.use_timer_bar()
    time_bar_duration = -1
    if survey.image_survey.answer_timer is not None and time_bar_enabled:
        time_bar_duration = survey.image_survey.answer_timer.seconds
    
    session["possible_answers"] = image_urls;
    session["time_bar_enabled"] = time_bar_enabled;
    
    return render_template("survey.html", **{
        "dataset_url" : survey.image_survey.image_server,
        "image_urls":image_urls,
        "time_bar_enabled": time_bar_enabled,
        "answer_duration": time_bar_duration,
        "question": survey.image_survey.question.model_dump(),
        "survey_duration": survey.image_survey.duration_seconds if survey.image_survey.duration_seconds is not None else -1,
        "accent_color": f"--accent_color:{survey.accent_color}", # Css rule to set the custom survey accent
        "survey_post_url": f"/survey/{survey.identifier}/{current_step}",
    })

def post_handler(request: Request, survey: Survey) -> Response | None:
    class Image(BaseModel):
        image: str = Field()
        chosen: bool = Field()
    
    class Answer(BaseModel):
        index: int = Field()
        variables: Dict[str, str] = Field()
        images: List[Image] = Field(min_length=2,max_length=2)
        timeBarEnabled: bool = Field()
        userId: str = Field(default="null_id")
    
        # image: str = Field()
        # chosen: bool = Field()
        # userId: str = Field() # maybe remove this
    
        def to_dictionary(self):
            return {
                "index": self.index,
                "variables": self.variables,
                "images": self.images,
                "timeBarEnabled": self.timeBarEnabled,
                "userId": self.userId,
    
                # "image": self.image,
                # "chosen": self.chosen,
                # "userId": self.userId,
                # "questionVariables": self.questionVariables,
            }

    try:
        # Each answer is a pair containing both
        # options to choose from
        try:
            answers = request.get_json()
        except:
            # Custom error message when invalid json
            raise Exception("The request does not have a proper body.")

        current_image_index = 0

        # Note: While it is rare that anyone would try to "fake spam" survey
        # data, we check each answer structure and types, to ensure they
        # are actually the correct ones.
        clean_answers = []
        for answer in answers:
            try:
                clean_answer = Answer(**answer)
            except Exception:
                raise Exception("The answer format is wrong.") # Raise custom exception, instead of Pydantic one

            for i in range(0, 2):
                # Ensure the image is the set of the user
                valid = session["possible_answers"][current_image_index] == clean_answer.images[i].image

                # Ensure the time bar enabled is also correct
                valid = valid and session["time_bar_enabled"] == clean_answer.timeBarEnabled

                if valid:
                    current_image_index += 1
                else:
                    raise Exception("The answers provided do not match with the user-specific ones.")

            # If both are valid:
            clean_answer.userId = session["user_id"]
            clean_answers.append(clean_answer.model_dump())

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
