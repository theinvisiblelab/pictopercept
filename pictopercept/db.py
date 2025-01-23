from pymongo import MongoClient
from os import environ
import logging
import errno
import mongomock

client = None

def db_init(debug_mode):
    global client

    mongodb_uri = environ.get("MONGODB_URI", "mongodb://localhost:27017/")

    if debug_mode:
        logging.getLogger(__name__).warning("[INFO] MongoDB started in-memory.")
        client = mongomock.MongoClient(mongodb_uri, maxPoolSize=200)
    else:
        client = MongoClient(mongodb_uri, maxPoolSize=200)

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
        
def db_save_question_survey(survey_content, survey_id):
    global client
    client["main_db"][f"{survey_id}_questions"].insert_one(survey_content)

def db_save_image_survey(survey_content, survey_id):
    global client
    client["main_db"][f"{survey_id}_images"].insert_many(survey_content)

def db_query_all(table_name):
    global client
    if client is not None:
        results = client["main_db"][f"{table_name}_questions"].aggregate([
            {
                "$lookup": {
                    "from": f"{table_name}_images",
                    "localField": "userId",
                    "foreignField": "userId",
                    "as": "image_answers"
                }
            }
        ])

        final_data = []
        for result in results:
            if len(result["image_answers"]) == 0:
                continue

            result.pop("_id")
            for i in range(len(result["image_answers"])):
                result["image_answers"][i].pop("_id")

            final_data.append(result)

        return final_data
    else:
        logging.getLogger(__name__).error("[ERROR] DB Client is None.")
        return []
