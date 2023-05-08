import os
from dotenv import load_dotenv
import json

load_dotenv()  # loads the environment variables from .env file

MILVUS_CONNECTION_ARGS = {
    "host": os.getenv("MILVUS_HOST"),
    "port": os.getenv("MILVUS_PORT"),
}

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_DEPLOYMENT_NAME = os.getenv("EMBEDDING_DEPLOYMENT_NAME")

MQ_HOST = os.getenv("MQ_HOST")
MQ_PORT = os.getenv("MQ_PORT")
MQ_TOPIC = os.getenv("MQ_TOPIC")

DEFAULT_COLLECTION_NAME = 'know_more_txt'
DEFAULT_TEXT_FIELD = 'raw_text'

OSS_ENDPOINT = os.getenv("OSS_ENDPOINT")
ACCESSKEY_ID = os.getenv("ACCESSKEY_ID")
ACCESSKEY_SECRET = os.getenv("ACCESSKEY_SECRET")
BUCKET_NAME = os.getenv("BUCKET_NAME")

TEMP_DIR = os.getenv("TEMP_DIR")

EMBED_FINISH_NOTIFY_STATION = os.getenv("EMBED_FINISH_NOTIFY_STATION")
EMBED_FINISH_NOTIFY_PRODUCER_NAME = os.getenv("EMBED_FINISH_NOTIFY_PRODUCER_NAME")
EMBED_CONSUMER = os.getenv("EMBED_CONSUMER")
EMBED_CONSUMER_GROUP = os.getenv("EMBED_CONSUMER_GROUP")
