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

# TODO: Handle CSRF properly
#@csrf_exempt
def survey_post_page(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request'}, status = 400)

    try:
        answers = json.loads(request.body.decode('utf-8'))
        # TODO: Sanitize body

        possible_answers_index = 0
        # Each answer is a pair containing both
        # options to choose from
        for answer in answers:
            print(answer)

            image0 = answer[0]["image"]
            image1 = answer[1]["image"]

            # Ensure both options are the user's available answers
            valid0 = request.session["possible_answers"][possible_answers_index] == image0
            valid1 = request.session["possible_answers"][possible_answers_index+1] == image1

            # Ensure only one of them is chosen
            valid = valid0 and valid1 and (answer[0]["chosen"] != answer[1]["chosen"])

            if valid:
                possible_answers_index += 2
            else:
                return JsonResponse({'error': 'Invalid answers'}, status = 500)

        try:
            collection_name = request.session["survey_db_collection"]
            MAIN_DB[collection_name].insert_many(list(np.concatenate(answers)))
        except pymongo.errors.OperationFailure:
            print("There was an error inserting the answers...")
            return JsonResponse({'error': 'Error pushing answers.'}, status = 500)
        else:
            return JsonResponse({'status': 'Ok'})

    except Exception as e:
        return JsonResponse({'error': 'Error handling body data (' + str(e) +')'}, status = 500)
