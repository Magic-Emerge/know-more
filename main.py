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


MILVUS_CONNECTION_ARGS = {
    "host": "10.39.201.210",
    "port": "30530",
}
MILVUS_COLLECTION_NAME = 'badcase_default'
MILVUS_TEXT_FIELD = 'badcase_text_field_default'

os.environ["OPENAI_API_BASE"] = "http://10.8.0.12:8888/api/v1"
os.environ["OPENAI_API_KEY"] = "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"


app = FastAPI()
templates = Jinja2Templates(directory="templates")
vectorstore: Optional[VectorStore] = None


@app.on_event("startup")
async def startup_event():
    logging.info("loading vectorstore")
    if not Path("vectorstore.pkl").exists():
        raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
    with open("vectorstore.pkl", "rb") as f:
        global vectorstore
        vectorstore = pickle.load(f)

# @app.on_event("startup")
# async def startup_event():
#     global vectorstore, retriever, qa_chain

#     embeddings = OpenAIEmbeddings()
#     vs_db = Milvus.from_existing(
#         embedding=embeddings,
#         connection_args=MILVUS_CONNECTION_ARGS,
#         collection_name=MILVUS_COLLECTION_NAME,
#         text_field=MILVUS_TEXT_FIELD
#     )
#     vectorstore = vs_db

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

    uvicorn.run(app, host="0.0.0.0", port=9000)
