"""Main entrypoint for the app."""
import os
import logging
import streamlit as st
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.schema import(
     SystemMessage,
     AIMessage,
     HumanMessage
)
from dotenv import load_dotenv
import pickle
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain.vectorstores import VectorStore

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from query_data import get_chain
from schemas import ChatResponse

# app = FastAPI()
# templates = Jinja2Templates(directory="templates")
# vectorstore: Optional[VectorStore] = None


# @app.on_event("startup")
# async def startup_event():
#     logging.info("loading vectorstore")
#     if not Path("vectorstore.pkl").exists():
#         raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
#     with open("vectorstore.pkl", "rb") as f:
#         global vectorstore
#         vectorstore = pickle.load(f)

st.set_page_config(
        page_title="Alcade - The AI Game",
        page_icon="🪐"
    )

def init():
    load_dotenv()
    # Load the OpenAI API key from the environment variable
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OpenAI API Key is not set")
        exit(1)
    else:
        print("OpenAI API Key is set")

def load_vectorstore():
    st.write("loading vectorstore")
    if not Path("vectorstore.pkl").exists():
        raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
    with open("vectorstore.pkl", "rb") as f:
        global vectorstore
        vectorstore = pickle.load(f)

# @app.get("/")
# async def get(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.websocket("/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     question_handler = QuestionGenCallbackHandler(websocket)
#     stream_handler = StreamingLLMCallbackHandler(websocket)
#     chat_history = []
#     #qa_chain = get_chain(vectorstore, question_handler, stream_handler)
#     # Use the below line instead of the above line to enable tracing
#     # Ensure `langchain-server` is running
#     qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)

#     while True:
#         try:
#             # Receive and send back the client message
#             question = await websocket.receive_text()
#             resp = ChatResponse(sender="you", message=question, type="stream")
#             await websocket.send_json(resp.dict())

#             # Construct a response
#             start_resp = ChatResponse(sender="bot", message="", type="start")
#             await websocket.send_json(start_resp.dict())

#             result = await qa_chain.acall(
#                 {"question": question, "chat_history": chat_history}
#             )
#             chat_history.append((question, result["answer"]))

#             end_resp = ChatResponse(sender="bot", message="", type="end")
#             await websocket.send_json(end_resp.dict())
#         except WebSocketDisconnect:
#             logging.info("websocket disconnect")
#             break
#         except Exception as e:
#             logging.error(e)
#             resp = ChatResponse(
#                 sender="bot",
#                 message="Sorry, something went wrong. Try again.",
#                 type="error",
#             )
#             await websocket.send_json(resp.dict())

def main():
    init()
    load_vectorstore()
    character_name = "Harry"

    chat = ChatOpenAI(temperature=0.3)

    #chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
           SystemMessage(content="""You are Hiren, a middle-aged vendor from the town of Smritiakrav. 
                                    You are currently painting geometric patterns on your fruit stall in an desperate effect to ward 
                                    off whatever is causing disappearance in your town. Your objective is to seek help from the person you are talking to, 
                                    an outsider who may possess the skills needed to unravel the mystery.""")
                                    ]
        
    doc_chain = get_chain(vectorstore, tracing=True)


    st. title("Alcade🪐 - The AI Game")
    st.header ("Chapter 1 : Arrival in Smritiakrav")
    st.write ("""As you ride towards Smritiakrav, the town on the edge of the Dharov kingdom, a sense of unease settles over you. The once bustling market now appears eerily quiet, with only a few souls traversing the ancient streets. An atmosphere of urgency lingers in the air, as if the town is holding its breath.
                Your eyes are drawn to the towering earth monument at the center of the town square, its weathered stone bearing the weight of history. Around it, people gather, fervently marking their homes and shops with vibrant symbols. Geometric patterns, cryptic glyphs, and vivid depictions of ancient stories adorn the walls, a desperate attempt to ward off an unseen threat."
                """)
    st.write ("The scent of fresh bread mingles with an undercurrent of tension in the air. Among the crowd, you notice a burly vendor hastily draws a symbol on his stall. Seeing you, he pauses and asks")
    st.write("Vendor: Hey Traveller! How can I help you? I'll complete my symbols later. Pardon my appearance, I assure you I can be quite reasonable" + "\n\n" + "You ("+(character_name)+") :")


    with st.sidebar:
        st.header("My Profile")
        image = Image.open('/Users/yellow/Documents/Code/Alcade/Alcade/Alcade/Profile picture/Harry Potter_Wizard.png') 
        st.image(image) 
        st.subheader("Harry Potter")
        #st.write("Race: Wizard")
        st.caption ("Backstory: He was orphaned young. His parents died in a magical accident when he was 8. He has a scar on hi sface from a failed potion attempt." )
        user_input = st.text_input("You say..", key="user_input")

        if user_input:
           #st.write (character_name + " (You) : " + user_input)
           st.session_state.messages.append(HumanMessage(content=user_input))
           context = doc_chain(user_input)
           #st.session_state.messages.append(SystemMessage(content=context))
           with st.spinner("Thinking..."):
                response = chat(st.session_state.messages)
           #st.write ("Hiren: " + response.content)
           st.session_state.messages.append(
               AIMessage(content=response.content))
           user_input = ""

    messages = st.session_state.get("messages", [])
    for i, msg in enumerate(messages[1:]):
        if i% 3 == 0:
            st.write ("Hiren: " + msg.content)
        if i% 3 == 1:
            st.write ("Harry"+ " (You) : " + msg.content)
            
    

if __name__ == "__main__":
    main ()
    #import streamlit
    #streamlit.run(streamlit run /Users/yellow/Documents/Code/chat-langchain_exp/main.py)
    #import uvicorn

    #uvicorn.run(app, host="0.0.0.0", port=9000)
