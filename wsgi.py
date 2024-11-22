import logging
from pictopercept import create_app
from os import environ
from dotenv import load_dotenv

from pictopercept.db import db_init
from pictopercept.survey import load_surveys

logging.getLogger(__name__).warning("[INFO] Loading .ENV file...")
load_dotenv()

logging.getLogger(__name__).warning("[INFO] Creating the Flask App..")
app = create_app()
app.config["MONGO_URI"] = environ.get("MONGODB_URI")

with app.app_context():
    logging.getLogger(__name__).warning("[INFO] Testing surveys...")
    load_surveys() # Ensure all surveys are valid before starting the server
    logging.getLogger(__name__).warning("[INFO] Testing MongoDB connection...")
    db_init() # Ensure initial MONGO_URI/Credentials are OK

if __name__ == "__main__":
    app.run()
