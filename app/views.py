from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from numpy import random
import pandas as pd

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
        image_urls.append("https://raw.githubusercontent.com/saurabh-khanna/pictopercept/refs/heads/main/data/fairface/nomargin/" + df.iloc[i]["file"])

    return render(request, "survey.html", {
        "image_urls":image_urls,
        "occupations":occupations,
        "time_bar_enabled": random.choice([True, False])
    })
