import json
import logging

from flask import Request, Response, make_response, render_template, session

from pictopercept.db import db_save_question_survey
from pictopercept.lib.common_types import MAX_USER_ID_LEN, BaseSurvey

def get_handler(survey: BaseSurvey, current_step: str):
    return render_template("regular_questions.html", ** {
        "accent_color": f"--accent_color:#ff4b4b",
        "questions": survey.generate_regular_survey().questions,
        "survey_post_url": f"/survey/{survey.metadata.identifier}/{current_step}",
    })

def post_handler(request: Request, survey: BaseSurvey) -> Response | None:
    data = request.get_json()

    if len(survey.metadata.regular_questions) is not len(data):
        return make_response("Incorrect answer format.", 400)

    clean_answers = []
    errors = {}

    try:
        for i, [question, answer] in enumerate(zip(survey.metadata.regular_questions, data)):
            result = question.validate(answer)

            if isinstance(result, str):
                errors[str(i)] = result
                continue;

            result["kind"] = question.kind
            clean_answers.append(result)

        if len(errors) == 0:
            try:
                db_save_question_survey({
                    "userId": session["user_id"][:MAX_USER_ID_LEN],
                    "isProlific": session["prolific"],
                    "answers": clean_answers
                }, session["survey_db_collection"])
            except Exception as e:
                logging.getLogger(__name__).error("[ERROR] Error saving user answers into the MongoDB database.")
                logging.getLogger(__name__).error("[ERROR] " + str(e))
                return make_response(f"There was an error with the database while saving your answers.", 500)
            else:
                return None
        else:
            return make_response(errors, 400)

    except Exception as e:
        return make_response(json.dumps({"-1":"Incorrect answer format.", "reason": str(e)}), 400)
