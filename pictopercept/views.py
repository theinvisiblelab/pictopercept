from typing import Dict
from flask import make_response, render_template, request, session
from flask import Blueprint
import logging
from pydantic import Field, BaseModel
from pictopercept.db import db_save_survey
from pictopercept.survey import get_survey, get_surveys

# Route definitions
main_routes = Blueprint('main', __name__)

@main_routes.route("/", methods=['GET'])
def index():
    content = "<h3>Available surveys</h3><ul>"
    for key in get_surveys().keys():
        content += f"<li>Survey of {key}, <a href='/survey/{key}'>here</a></li>"
    content += "</ul>"

    return make_response(content, 200)

@main_routes.route("/survey/<id>", methods=['GET'])
def survey_index(id):
    survey = get_survey(id)
    if survey is not None and survey.enabled:
        return render_template("index.html", ** {
            "survey_description": survey.big_description,
            "survey_id": id,
            "accent_color": f"--accent_color:{survey.accent_color}" # Css rule to set the custom survey accent
        })
    else:
        return make_response("There is no default survey set, the survey was not found, or it is not enabled.", 404)

@main_routes.route("/survey/<id>/take", methods=['GET'])
def survey(id):
    survey = get_survey(id)
    if survey is not None:
        df = survey.load_datasets()

        image_urls = df[:200]["file"].tolist()
        time_bar_enabled = survey.use_timer_bar()
        time_bar_duration = -1
        if survey.answer_timer is not None and time_bar_enabled:
            time_bar_duration = survey.answer_timer.seconds

        session["survey_db_collection"] = survey.db_collection
        session["possible_answers"] = image_urls;
        session["time_bar_enabled"] = time_bar_enabled;

        return render_template("survey.html", **{
            "dataset_url" : survey.image_server,
            "image_urls":image_urls,
            "time_bar_enabled": time_bar_enabled,
            "answer_duration": time_bar_duration,
            "question": survey.question.model_dump(),
            "survey_duration": survey.duration_seconds if survey.duration_seconds is not None else -1,
            "sustantive": survey.sustantive,
            "accent_color": f"--accent_color:{survey.accent_color}" # Css rule to set the custom survey accent
        })
    else:
        r = make_response("Survey not found.")
        r.status_code = 404
        return r

class Answer(BaseModel):
    index: int = Field()
    image: str = Field()
    chosen: bool = Field()
    userId: str = Field() # maybe remove this
    timeBarEnabled: bool = Field()
    questionVariables: Dict[str, str] = Field()

    def to_dictionary(self):
        return {
            "index": self.index,
            "image": self.image,
            "chosen": self.chosen,
            "userId": self.userId,
            "timeBarEnabled": self.timeBarEnabled,
            "questionVariables": self.questionVariables,
        }

@main_routes.route("/survey/end", methods=['POST'])
def survey_post_page():
    try:
        # Each answer is a pair containing both
        # options to choose from
        try:
            answers = request.get_json()
        except:
            # Custom error message when invalid json
            raise Exception("The request does not have a proper body.")


        current_answer_index = 0

        # Note: While it is rare that anyone would try to "fake spam" survey
        # data, we check each answer structure and types, to ensure they
        # are actually the correct ones.
        clean_answers = []
        for answer in answers:
            for i in range(0, 2):
                try:
                    clean_answer = Answer(**answer[i])
                except Exception:
                    raise Exception("The answer format is wrong.") # Raise custom exception, instead of Pydantic one

                # Ensure the image is the set of the user
                valid = session["possible_answers"][current_answer_index] == clean_answer.image

                # Ensure the time bar enabled is also correct
                valid = valid and session["time_bar_enabled"] == clean_answer.timeBarEnabled

                if valid:
                    # Append the answer in Dict format (which is needed for MongoDB or any document-DB)
                    clean_answers.append(clean_answer.model_dump())
                    current_answer_index += 1
                else:
                    raise Exception("The answers provided do not match with the user-specific ones.")

        try:
           #db_save_survey(clean_answers, session["survey_db_collection"])
           db_save_survey(clean_answers, "test_collection2")
        except Exception as e:
            logging.getLogger(__name__).error("[ERROR] Error saving user answers into the MongoDB database.")
            logging.getLogger(__name__).error("[ERROR] " + str(e))
            return make_response(f"There was an error with the database while saving your answers.", 500)
        else:
            # Clear session
            del session["survey_db_collection"]
            del session["possible_answers"]
            del session["time_bar_enabled"]
            session.clear()

            return make_response("Ok", 200)
    except Exception as e:
            return make_response(f"Error validating the answers: '{str(e)}'", 400)
