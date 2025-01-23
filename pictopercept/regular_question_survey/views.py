import json
import logging

from flask import Request, Response, make_response, render_template

from . import validator
from pictopercept.survey_loader import Survey

def get_handler(survey: Survey, current_step: str):
    survey_questions = []
    if survey is not None:
        survey_questions = survey.regular_survey
    
    return render_template("regular_questions.html", ** {
        "accent_color": f"--accent_color:#ff4b4b",
        "questions": survey_questions,
        "survey_post_url": f"/survey/{survey.identifier}/{current_step}",
    })

def post_handler(request: Request, survey: Survey) -> Response | None:
    data = request.get_json()
    logging.getLogger(__name__).warning("[INFO] Posted data: " + str(data))

    if len(survey.regular_survey) is not len(data):
        return make_response("Incorrect answer format.", 400)

    clean_answers = []
    errors = {}

    try:
        for i, [question, answer] in enumerate(zip(survey.regular_survey, data)):
            match question.question_type:
                case "MultipleChoice":
                    result = validator.validate_multiple_choice(question, answer)
                case "SingleChoice":
                    result = validator.validate_single_choice(question, answer)
                case "Matrix":
                    result = validator.validate_matrix(question, answer)
                case "AgreementScale":
                    result = validator.validate_agreement_scale(question, answer)
                case "OpenShort":
                    result = validator.validate_open_short(question, answer)
                case _:
                    raise Exception("")

            if isinstance(result, str):
                errors[str(i)] = result
                continue;

            clean_answers.append(result)

        if len(errors) == 0:
            # TODO: Push the data into the DB
            # Then, continue with the pairwise OR end the survey
            return None
        else:
            return make_response(errors, 400)

    except Exception as e:
        return make_response(json.dumps({"-1":"Incorrect answer format.", "reason": str(e)}), 400)
