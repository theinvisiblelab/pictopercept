from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.index_page, name="index_page"),
    path('survey', view=views.survey_page, name="survey_page"),
    path('post-survey', view=views.survey_post_page, name="survey_post_page")
]
