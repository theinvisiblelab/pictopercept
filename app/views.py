import uuid
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.conf import settings
from numpy import random
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import json

BASE_DIR = settings.BASE_DIR

def index_page(request):
    return render(request, "index.html", {})

def survey_page(request):
    file_paths = [
        BASE_DIR / "./app/datasets/fairface/label_train.csv",
        BASE_DIR / "./app/datasets/fairface/label_val.csv"
    ]
    df = pd.concat((pd.read_csv(file) for file in file_paths), ignore_index=True)
    df = df[~df['age'].isin(['0-2', '3-9', '10-19'])]  # drop non-adults
    df = df.sample(frac=1).reset_index(drop=True)  # shuffle rows

    image_urls = []
    occupations = ['a doctor', 'a lawyer', 'a nurse', 'an author', 'a teacher', 'an engineer', 'a scientist', 'a chef', 'an artist', 'an architect', 'a pilot', 'a journalist', 'a dentist', 'a therapist', 'an accountant', 'a musician', 'a designer',
                'a programmer', 'a pharmacist', 'a plumber', 'an electrician', 'a librarian', 'an analyst', 'a consultant', 'an entrepreneur', 'a researcher', 'a technician', 'an editor', 'a translator', 'a veterinarian', 'a social worker', 'a photographer']

    for i in range(0, 200):
        image_urls.append(df.iloc[i]["file"])

    time_bar_enabled = random.choice([True, False])

    # User ID might not be needed
    request.session["user_id"] = str(uuid.uuid4())
    request.session["possible_answers"] = image_urls;
    request.session["time_bar_enabled"] = str(time_bar_enabled);

    return render(request, "survey.html", {
        "dataset_url" : "https://raw.githubusercontent.com/saurabh-khanna/pictopercept/refs/heads/main/data/fairface/nomargin/",
        "image_urls":image_urls,
        "occupations":occupations,
        "time_bar_enabled": time_bar_enabled,
    })

# TODO: Handle CSRF properly
@csrf_exempt
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
            image0 = answer[0]["image"]
            image1 = answer[1]["image"]

            # Ensure both options are the user's available answers
            valid0 = request.session["possible_answers"][possible_answers_index] == image0
            valid1 = request.session["possible_answers"][possible_answers_index+1] == image1

            # Ensure only one of them is chosen
            valid = valid0 and valid1 and (answer[0]["chosen"] != answer[1]["chosen"])

            if valid:
                possible_answers_index += 2;
            else:
                return JsonResponse({'error': 'Invalid answers'}, status = 500)

        # TODO: Post results to DB
        return JsonResponse({'status': 'Ok'})
    except:
        return JsonResponse({'error': 'Error handling body data'}, status = 500)
