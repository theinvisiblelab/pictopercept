from typing import Dict, List
import uuid
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.conf import settings
from numpy import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
import pandas as pd
import json
import numpy as np

from os import environ
from pydantic import BaseModel, Field
import pymongo

from app.survey import Survey, load_survey, load_surveys

def connectMongoDB():
    try:
        db_url = f'mongodb+srv://{environ.get("MONGODB_USERNAME")}:{environ.get("MONGODB_PASSWORD")}@{environ.get("MONGODB_SERVER")}/?retryWrites=true&w=majority&appName=Pictopercept'
        client = pymongo.MongoClient(db_url)
        client.admin.command("ping")
        return client
    except Exception as e:
        print("Couldn't connect to MongoDB database. Reason: ", e)
        exit(1)

DB_CLIENT = connectMongoDB()
MAIN_DB = DB_CLIENT["main_db"]

BASE_DIR = settings.BASE_DIR

@xframe_options_exempt
def index_page(request):
    return render(request, "index.html", {})


@xframe_options_exempt
def survey_page(request):
    survey = load_survey("jobs")
    if isinstance(survey, Survey):
        df = survey.load_datasets()

        image_urls = df[:200]["file"].tolist()
        time_bar_enabled = survey.use_timer_bar()
        time_bar_duration = -1
        if survey.answer_timer is not None and time_bar_enabled:
            time_bar_duration = survey.answer_timer.seconds

        # User ID might not be needed
        request.session["user_id"] = str(uuid.uuid4())
        request.session["survey_db_collection"] = survey.db_collection
        request.session["possible_answers"] = image_urls;
        request.session["time_bar_enabled"] = str(time_bar_enabled);

        return render(request, "survey.html", {
            "dataset_url" : survey.image_server,
            "image_urls":image_urls,
            "time_bar_enabled": time_bar_enabled,
            "answer_duration": time_bar_duration,
            "question": survey.question.as_json(),
            "survey_duration": survey.duration_seconds if survey.duration_seconds is not None else -1,
            "sustantive": survey.sustantive
        })
    else:
        return HttpResponse(b"Survey not found.");
 
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

def survey_post_page(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request'}, status = 400)

    try:
        # Each answer is a pair containing both
        # options to choose from
        answers = json.loads(request.body.decode('utf-8'))

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
                valid = request.session["possible_answers"][current_answer_index] == clean_answer.image

                # Ensure the time bar enabled is also correct
                valid = valid and request.session["time_bar_enabled"] == clean_answer.timeBarEnabled

                if valid:
                    # Append the answer in Dict format (which is needed for MongoDB or any document-DB)
                    clean_answers.append(clean_answer.model_dump())
                    current_answer_index += 1
                else:
                    raise Exception("The answers provided do not match with the user-specific ones.")

        try:
            collection_name = request.session["survey_db_collection"]
            MAIN_DB[collection_name].insert_many(clean_answers)
        except pymongo.errors.OperationFailure:
            return JsonResponse({'error': 'There was an error with the database while saving your answers.'}, status = 500)
        else:
            # Clear session
            del request.session["user_id"]
            del request.session["survey_db_collection"]
            del request.session["possible_answers"]
            del request.session["time_bar_enabled"]
            request.session.modified = True

            return JsonResponse({'status': 'Ok'})
    except Exception as e:
        return JsonResponse({'error': f"Error validating the answers: '{str(e)}'"}, status = 400)
