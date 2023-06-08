"""Main entrypoint for the app."""
import logging
import pickle
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain.vectorstores import VectorStore
from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from query_data import get_chain
from schemas import ChatResponse

from langchain.schema import(
     SystemMessage,
     AIMessage,
     HumanMessage
)
from langchain.chat_models import ChatOpenAI


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


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    chat_history = []
    #qa_chain = get_chain(vectorstore, question_handler, stream_handler)
    # Use the below line instead of the above line to enable tracing
    # Ensure `langchain-server` is running
    qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)


    chat = ChatOpenAI(temperature=0.3)
    messages = [
           SystemMessage(content="""You are Hiren, a middle-aged vendor from the town of Smritiakrav. 
                                    You are currently painting geometric patterns on your fruit stall in an desperate effect to ward 
                                    off whatever is causing disappearance in your town. Your objective is to seek help from the person you are talking to, 
                                    an outsider who may possess the skills needed to unravel the mystery.""")
                                    ]


    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.dict())
            print (question)
            print (resp)
            messages.append(HumanMessage(content=question))

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            print (start_resp)

            result = await qa_chain.acall(
                {"question": question, "chat_history": chat_history}
            )
            chat_history.append((question, result["answer"]))

            print (result)

            messages.append(SystemMessage(content=result))
            response = chat(messages)
            messages.append(AIMessage(content=response.content))

            end_resp = ChatResponse(sender="bot", message=response.content, type="end")
            await websocket.send_json(end_resp.dict())
            print (end_resp)
            print (response)
            print (response.content)

            ##main_resp = {sender: "Hiren", message: response.content, type: "end"}
            ##await websocket.send_json(main_resp.dict())



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

