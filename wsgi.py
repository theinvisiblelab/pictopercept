import logging
from pictopercept import create_app
from os import environ
from dotenv import load_dotenv

from pictopercept.survey import load_surveys

load_dotenv()
app = create_app()
load_surveys() # Ensure all surveys are valid before starting the server

if __name__ == "__main__":
    app.run()
