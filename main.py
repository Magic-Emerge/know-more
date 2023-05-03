"""Main entrypoint for the app."""
import os
import logging
from typing import Optional
import traceback
import pickle
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

from langchain.chains.base import Chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import VectorStore
from langchain.schema import BaseRetriever
from milvus import Milvus
from langchain.chains import ConversationalRetrievalChain, RetrievalQAWithSourcesChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.chains.qa_with_sources.map_reduce_prompt import (
    COMBINE_PROMPT,
    EXAMPLE_PROMPT,
    QUESTION_PROMPT,
)

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from query_data_extend import get_chain
from schemas import ChatResponse
import os
from dotenv import load_dotenv
from __future__ import annotations
import asyncio
from memphis import Memphis, Headers, MemphisError, MemphisConnectError, MemphisHeaderError, MemphisSchemaError

load_dotenv()  # loads the environment variables from .env file

MILVUS_CONNECTION_ARGS = {
    "host": "10.39.201.210",
    "port": "30530",
}
MILVUS_COLLECTION_NAME = 'badcase_default'
MILVUS_TEXT_FIELD = 'badcase_text_field_default'

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# os.environ["OPENAI_API_BASE"] = "http://10.8.0.12:8888/api/v1"
# os.environ["OPENAI_API_KEY"] = "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"

app = FastAPI()
templates = Jinja2Templates(directory="templates")
vectorstore: Optional[VectorStore] = None


# @app.on_event("startup")
# async def startup_event():
#     logging.info("loading vectorstore")
#     if not Path("vectorstore.pkl").exists():
#         raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
#     with open("vectorstore.pkl", "rb") as f:
#         global vectorstore
#         vectorstore = pickle.load(f)


async def listener_mq():
    async def msg_handler(msgs, error, context):
        try:
            for msg in msgs:
                print("message: ", msg.get_data())
                await msg.ack()
                headers = msg.get_headers()
                if error:
                    print(error)
        except (MemphisError, MemphisConnectError, MemphisHeaderError) as e:
            print(e)
            return

    try:
        memphis = Memphis()
        await memphis.connect(host="10.8.0.12", username="know_more", password="23l1df5sn")

        consumer = await memphis.consumer(station_name="file_embeddings", consumer_name="file_embeddings_consumer",
                                          consumer_group="file_embeddings_consumer_group")
        consumer.set_context({"key": "value"})
        consumer.consume(msg_handler)
        # Keep your main thread alive so the consumer will keep receiving data
        await asyncio.Event().wait()

    except (MemphisError, MemphisConnectError) as e:
        print(e)

    finally:
        await memphis.close()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    chat_history = []
    qa_chain = get_chain(vectorstore, question_handler, stream_handler)
    # Use the below line instead of the above line to enable tracing
    # Ensure `langchain-server` is running
    # qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)

    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            result = await qa_chain.acall(
                {"question": question, "chat_history": chat_history}
            )
            chat_history.append((question, result["answer"]))

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.dict())


if __name__ == "__main__":
    import uvicorn
    # 监听mq
    listener_mq()
    uvicorn.run(app, host="0.0.0.0", port=9000)
