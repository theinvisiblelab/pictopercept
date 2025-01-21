import logging
from pictopercept import create_app
from os import environ
from dotenv import load_dotenv

from pictopercept.db import db_init
from pictopercept.survey import load_surveys

logging.getLogger(__name__).warning("[INFO] Loading .ENV file...")
load_dotenv()

# Ensure all necessary environment variables are set
def ensure_env(env_key):
    if not env_key in environ:
        logging.getLogger(__name__).critical(f"[ERROR] {env_key} is not set. Exiting...")
        exit(1)

ensure_env("MONGODB_URI")
ensure_env("FLASK_SECRET_KEY")
ensure_env("FETCH_PASSWORD")

# Create the Flask app itself
logging.getLogger(__name__).warning("[INFO] Creating the Flask App..")
app = create_app()

# Used by session and CSRF token.
# Should be long and random.
# It should be set as ENV variable once, so all
# gunicorn threads/workers (if using more than one) use the same.
app.config["SECRET_KEY"] = environ.get("FLASK_SECRET_KEY")

with app.app_context():
    logging.getLogger(__name__).warning("[INFO] Testing surveys...")
    load_surveys() # Ensure all surveys are valid before starting the server
    logging.getLogger(__name__).warning("[INFO] Testing MongoDB connection...")
    db_init(app.debug) # Ensure initial MONGODB_URI/Credentials are OK

if __name__ == "__main__":
    app.run()
