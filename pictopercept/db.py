import json
from os import environ
import logging
import errno
import mongomock

from flask import abort
from pymongo import MongoClient

from pictopercept.lib.survey_manager import get_survey

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

def db_query_all(table_name, chunk_size: int):
    # Recommended chunk_size between 50-300
    global client

    skip = 0
    first_result = True

    if client is not None:
        if get_survey(table_name) is None:
            abort(404)

        yield '{"data": ['

        while True:
            results = client["main_db"][f"{table_name}_questions"].aggregate([
                {
                    "$lookup": {
                        "from": f"{table_name}_images",
                        "localField": "userId",
                        "foreignField": "userId",
                        "as": "image_answers"
                    }
                },
                {"$skip": skip},
                {"$limit": chunk_size}
            ])

            chunk_results = list(results)
            if len(chunk_results) == 0:
                break

            for result in chunk_results:
                out = ", "
                if first_result:
                    out = ""
                    first_result = False

                if len(result["image_answers"]) == 0:
                    continue

                # Remove MongoDB id object
                result.pop("_id")
                for image_answer in result["image_answers"]:
                    image_answer.pop("_id")
                    # Drop extra info, as the parent object itself already has it
                    image_answer.pop("userId", None) 
                    image_answer.pop("isProlific", None)

                out += json.dumps(result)
                yield out
            skip += chunk_size
        yield "]\n}"
    else:
        logging.getLogger(__name__).error("[ERROR] DB Client is None.")
        return []

def db_query_image_answers(table_name, chunk_size: int):
    # Recommended chunk_size between 50-300
    global client

    skip = 0
    first_result = True

    if client is not None:
        if get_survey(table_name) is None:
            abort(404)

        yield '{"data": ['

        while True:
            results = client["main_db"][f"{table_name}_images"].aggregate([
                {"$skip": skip},
                {"$limit": chunk_size}
            ])

            chunk_results = list(results)
            if len(chunk_results) == 0:
                break

            for result in chunk_results:
                out = ", "
                if first_result:
                    out = ""
                    first_result = False

                # Remove MongoDB id object
                result.pop("_id")

                out += json.dumps(result)
                yield out
            skip += chunk_size
        yield "]\n}"
    else:
        logging.getLogger(__name__).error("[ERROR] DB Client is None.")
        return []
