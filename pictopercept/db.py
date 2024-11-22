from pymongo import MongoClient
from os import environ
import logging
import errno

client = None

def db_init():
    global client
    client = MongoClient(environ.get("MONGODB_URI"), maxPoolSize=200)

    try:
        result = client.admin.command("ping")
        if int(result.get("ok")) == 1:
            logging.getLogger(__name__).warning("[INFO] MongoDB connection OK.")
        else:
            raise Exception("Got a non 1 OK from MongoDB.")
    except Exception as e:
        logging.getLogger(__name__).error("[ERROR] Could not connect to the MongoDB database. Are the credentials/URI ok?")
        logging.getLogger(__name__).error("[ERROR] " + str(e))
        exit(errno.EINTR)

def db_save_survey(survey_content, table_name):
    global client
    client["main_db"][table_name].insert_many(survey_content)
