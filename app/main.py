"""Main entrypoint for the app."""
import logging

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import threading

from app.event.file_embeddings import file_embeddings_mq
from app.api.routes.assistant_qa import websocket_endpoint

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#
# @app.on_event("startup")
# async def startup_event():
#     # # 监听mq
#     # print("started memphis mq")
#     logging.info("async to start mq")
#     consumer_thread = threading.Thread(target=await file_embeddings_mq())
#     consumer_thread.start()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 支持websockt
app.add_websocket_route(path="/chat", route=websocket_endpoint)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
