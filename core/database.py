import os
import pymongo
from dotenv import load_dotenv

load_dotenv()


def setup_db():
    port = int(os.environ.get("DATABASE_PORT", 27017))
    user = os.environ.get("DATABASE_USER")
    host = os.environ.get("DATABASE_HOST")
    password = os.environ.get("DATABASE_PASSWORD")
    db_name = os.environ.get("DATABASE_NAME")
    auth_mechanism = os.environ.get("DATABASE_AUTH_MECHANISM", "DEFAULT")
    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource={db_name}&authMechanism={auth_mechanism}"
    client = pymongo.MongoClient(uri)
    return client[db_name]


db_client = setup_db()
