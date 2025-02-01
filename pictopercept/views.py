import os
import uuid
import logging

from flask import Blueprint, abort, make_response, redirect, render_template, request, send_file, session 
from numpy import random

from pictopercept.db import db_query_all, db_query_image_answers
from pictopercept.lib.common_types import BaseSurvey
from pictopercept.lib.survey_manager import get_survey, get_surveys
import pictopercept.lib.image_survey.handlers as image_handlers
import pictopercept.lib.regular_question_survey.handlers as regular_question_handlers

def get_survey_or_404(id) -> BaseSurvey:
    survey = get_survey(id)
    if survey is None:
        abort(404, "The survey was not found, or it is not enabled.")
    return survey

# Route definitions
main_routes = Blueprint('main', __name__)

@main_routes.route("/", methods=['GET'])
def index():
    content = "<h3>This is a temporal index. Select one survey:</h3><ul>"
    for key in get_surveys().keys():
        content += f"<li>Survey of {key}, <a href='/survey/{key}'>here</a></li>"
    content += "</ul>"

    return make_response(content, 200)

@main_routes.route("/survey/<id>", methods=['GET'])
def survey_index(id):
    survey = get_survey_or_404(id)

    return render_template("index.html", ** {
        "survey_description": survey.metadata.big_description,
        "survey_id": id,
        "accent_color": f"--accent_color:{survey.metadata.accent_color}" # Css rule to set the custom survey accent
    })

@main_routes.route("/survey/<id>/thanks", methods=['GET'])
def survey_thanks(id):
    _ = get_survey_or_404(id)
    session.clear()
    return make_response("<h1>Thanks</h1><p>Thanks for completing the survey. Your answers have been saved.</p>", 200)

@main_routes.route("/survey/<id>/take", methods=['GET'])
def survey_step_get(id):
    survey = get_survey_or_404(id)

    step = int(session.get("step", "1"))

    match step:
        case 1:
            # Clear/reset the user's session
            session.clear()
            session["step"] = 1
            session["survey_db_collection"] = survey.metadata.identifier

            prolific_id = request.args.get("PROLIFIC_PID")

            if prolific_id is not None:
                session["user_id"] = prolific_id
                session["prolific"] = True
            else:
                session["user_id"] = str(uuid.uuid4())
                session["prolific"] = False

            if survey.metadata.regular_questions_enabled:
                session["questions_first"] = bool(random.choice([True, False]))
            else:
                session["questions_first"] = False
        case 2:
            # End survey if regular questions are disabled
            if not survey.metadata.regular_questions_enabled:
                return redirect(f"/survey/{id}/thanks")
        case 3:
            return redirect(f"/survey/{id}/thanks")

    if (session["questions_first"] and step == 1) or (not session["questions_first"] and step == 2):
        return regular_question_handlers.get_handler(survey)
    else:
        return image_handlers.get_handler(survey)

@main_routes.route("/survey/<id>", methods=['POST'])
def survey_step_post(id):
    survey = get_survey_or_404(id)

    # Ensure valid session
    if session.get("user_id") is None:
        logging.getLogger(__name__).error("[ERROR] User tried posting data without a session.")
        return make_response("Cannot post data without an active survey session.", 400)

    step = session["step"]

    if step == 2 and not survey.metadata.regular_questions_enabled:
        abort(400)

    if (session["questions_first"] and step == 1) or (not session["questions_first"] and step == 2):
        error_response = regular_question_handlers.post_handler(request, survey)
    else:
        error_response = image_handlers.post_handler(request, survey)

    if error_response is None:
        if step == 1:
            session["step"] = 2
        elif step == 2:
            session["step"] = 3 # "Thanks" page

        return {} # 200 OK
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
    if survey_name not in get_surveys():
        return make_response("Survey not found.", 404)

    chunk_size = 100
    if arguments.get("chunk_size") is not None:
        chunk_size = int(arguments["chunk_size"])

    fetch_mode = "all"
    if arguments.get("mode") is not None:
        fetch_mode = arguments["mode"]

    if fetch_mode == "all":
        return db_query_all(survey_name, chunk_size), {
            "Content-Type": "application/json",
            "Content-Disposition": "attachment",
            "filename": "data.json"
        }
    elif fetch_mode == "images_only":
        return db_query_image_answers(survey_name, chunk_size), {
            "Content-Type": "application/json",
            "Content-Disposition": "attachment",
            "filename": "data.json"
        }
    else:
        abort(400)

@main_routes.route("/img/<answer_index>/<side>", methods=['GET'])
def get_cfd_image(answer_index, side):
    if session.get("generated_survey") is None:
        abort(404);

    if side != "l" and side != "r":
        abort(404);
    side = 0 if side == "l" else 1

    index = int(answer_index)
    if index < 0 or index >= len(session["generated_survey"]["pair_questions"]):
        abort(404);

    image_name = session["generated_survey"]["pair_questions"][index]["images"][side]
    image_dataset_path = session["generated_survey"]["image_dataset_path"]
    image_path = f"{image_dataset_path}/{image_name}"

    # Survey specific image path logic could be implemented here later if needed
    # if session["generated_survey"]["survey_name"] == "occupations":
    #   image_path = "..."

    if not os.path.exists(image_path):
        abort(404)

    return send_file(image_path, mimetype="image/jpeg")
