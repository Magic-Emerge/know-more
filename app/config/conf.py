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

MQ_HOST = os.getenv("MQ_HOST")
MQ_PORT = os.getenv("MQ_PORT")
MQ_TOPIC = os.getenv("MQ_TOPIC")

DEFAULT_COLLECTION_NAME = 'know_more_txt'
DEFAULT_TEXT_FIELD = 'raw_text'
