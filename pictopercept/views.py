import json
import os
from numpy import random
import uuid
from flask import Blueprint, abort, make_response, render_template, request, session 
import logging

from pictopercept.db import db_query_all
import pictopercept.survey_loader as survey_loader
import pictopercept.regular_question_survey.views as regular_question_views
import pictopercept.image_survey.views as image_views

def get_survey_or_404(id):
    survey = survey_loader.get_survey(id)
    if survey is None or not survey.enabled:
        abort(404, "The survey was not found, or it is not enabled.")
    return survey

# Route definitions
main_routes = Blueprint('main', __name__)

@main_routes.route("/", methods=['GET'])
def index():
    content = "<h3>This is a temporal index. Select one survey:</h3><ul>"
    for key in survey_loader.get_surveys().keys():
        content += f"<li>Survey of {key}, <a href='/survey/{key}'>here</a></li>"
    content += "</ul>"

    return make_response(content, 200)

@main_routes.route("/survey/<id>", methods=['GET'])
def survey_index(id):
    survey = get_survey_or_404(id)

    return render_template("index.html", ** {
        "survey_description": survey.big_description,
        "survey_id": id,
        "accent_color": f"--accent_color:{survey.accent_color}" # Css rule to set the custom survey accent
    })

@main_routes.route("/survey/<id>/thanks", methods=['GET'])
def survey_thanks(id):
    _ = get_survey_or_404(id)
    session.clear()
    return make_response("<h1>Thanks</h1><p>Thanks for completing the survey. Your answers have been saved.</p>", 200)

@main_routes.route("/survey/<id>/<step>", methods=['GET'])
def survey_step_get(id, step):
    survey = get_survey_or_404(id)

    if step != "1" and step != "2":
        abort(404)

    if step == "1":
        # Clear/reset the user's session
        session.clear()
        session["user_id"] = str(uuid.uuid4())
        session["questions_first"] = bool(random.choice([True, False]))
        session["step_1_completed"] = False

    if step == "2":
        # Ensure valid session
        if session.get("user_id") is None:
            logging.warning("[WARNING] User visited step two without a session.")
            return make_response(f"It seems you don't have an active session. You can start the survey <a href=\"/survey/{id}/1\">here</a>.", 400)

        # Ensure step 1 is completed
        if not session["step_1_completed"]:
            logging.warning("[WARNING] User visited step two without completing step 1.")
            return make_response(f"It seems you haven't completed the survey's step one.. You can start again the survey <a href=\"/survey/{id}/1\">here</a>.", 400)

    if (session["questions_first"] and step == "1") or (not session["questions_first"] and step == "2"):
        return regular_question_views.get_handler(survey, step)
    else:
        return image_views.get_handler(survey, step)

@main_routes.route("/survey/<id>/<step>", methods=['POST'])
def survey_step_post(id, step):
    survey = get_survey_or_404(id)

    if step != "1" and step != "2":
        return make_response("", 404)
    
    # Ensure valid session
    if session.get("user_id") is None:
        logging.getLogger(__name__).error("[ERROR] User tried posting data without a session.")
        return make_response("Cannot post data without an active survey session.", 400)

    # Ensure step 1 is completed
    if step == "2" and not session["step_1_completed"]:
        logging.getLogger(__name__).error("[ERROR] User tried posting to step two without completing step one.")
        return make_response("Cannot post data to step two without completing step one.", 400)

    if (session["questions_first"] and step == "1") or (not session["questions_first"] and step == "2"):
        error_response = regular_question_views.post_handler(request, survey)
    else:
        error_response = image_views.post_handler(request, survey)

    if error_response is None:
        if step == "1":
            session["step_1_completed"] = True
            return make_response(json.dumps({
                "next_step": f"/survey/{id}/2"
            }), 200)
        else:
            return make_response(json.dumps({
                "next_step": f"/survey/{id}/thanks"
            }), 200)
    else:
        return error_response

@main_routes.route("/fetch", methods=['POST'])
def fetch_data():
    if not "FETCH_PASSWORD" in os.environ:
        return make_response("Fetch password is not set.", 500)

    if not request.is_json:
        return make_response("Invalid content type.", 400)

    try:
        arguments = request.get_json()
    except:
        return make_response("Could not decode the body JSON.", 400)

    if "pass" not in arguments or "survey_name" not in arguments:
        return make_response("The JSON is missing fields.", 400)

    if arguments["pass"] != os.environ["FETCH_PASSWORD"]:
        return make_response("Forbidden.", 403)

    survey_name = arguments["survey_name"]
    if survey_name not in survey_loader.get_surveys():
        return make_response("Survey not found.", 404)

    data = json.dumps(db_query_all(survey_name))

    response = make_response({"data": data}, 200)
    response.headers["Content-Type"] = "application/json"
    return response
