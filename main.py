"""Main entrypoint for the app."""
import logging

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
import threading

from app.event.file_embeddings import file_embeddings_mq
from app.vectors.query_data_extend import get_chain

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from app.schema.chat_response_schema import ChatResponse
import os
from dotenv import load_dotenv
import json

load_dotenv()  # loads the environment variables from .env file

MILVUS_CONNECTION_ARGS = {
    "host": os.getenv("MILVUS_HOST"),
    "port": os.getenv("MILVUS_PORT"),
}

MILVUS_COLLECTION_NAME = 'badcase_default'
MILVUS_TEXT_FIELD = 'badcase_text_field_default'

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    # # 监听mq
    # print("started memphis mq")
    logging.info("异步启动mq")
    consumer_thread = threading.Thread(target=await file_embeddings_mq())
    consumer_thread.start()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # data = await websocket.receive_text()
    # # Parse the data as JSON
    # params = json.loads(data)
    # # Do something with the received parameters
    # print("Received parameters:", params)

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
