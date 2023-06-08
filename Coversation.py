
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
#nltk.download("punkt")



import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.schema import(
     SystemMessage,
     AIMessage,
     HumanMessage
)
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

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

#def load_documents():
    #return docs


def main():
    init()
    character_name = "Harry"
#    docs = load_documents()
  
    root_dir = "/Users/yellow/Documents/Code/Alcade/Alcade/Alcade"
    pdf_folder_path = f'{root_dir}/Story/'
    print (os.listdir(pdf_folder_path))

#    # Multiple File loader
    loader = DirectoryLoader(pdf_folder_path, glob="*.pdf", show_progress=True)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    del documents
    print (len(docs))

    # Creating embeddings
    embeddings = HuggingFaceEmbeddings()

    # Storing in Vector Store DB
    db = Chroma.from_documents(documents, embeddings)
    persist_directory = 'db'

    vectordb = Chroma.from_documents(documents=docs,
                                     embedding=embeddings,
                                     persist_directory=persist_directory)
    vectordb.persist()
    vectordb = None
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    del vectordb 
    # Making a Retriever from Vector Store
    retriever = vectordb.as_retriever()
    #for testing
    First_user_input = "What are the symbols?"
    user_query = First_user_input
    docs = retriever.get_relevant_documents(user_query)
#    docs = db.similarity_search(user_query)
#    print (len(docs))
#    print (docs[0])

    retriever = create_retriever(vectordb)

    chat = ChatOpenAI(temperature=0.3)
    
    #Retriever Chain
#    doc_chain = RetrievalQA.from_chain_type(llm=OpenAI(), 
#                                  chain_type="stuff", 
#                                  retriever=retriever, 
#                                  return_source_documents=True)


    if "messages" not in st.session_state:
        st.session_state.messages = [
           SystemMessage(content="""You are Hiren, a middle-aged vendor from the town of Smritiakrav. 
                                    You are currently painting geometric patterns on your fruit stall in an desperate effect to ward 
                                    off whatever is causing disappearance in your town. Your objective is to seek help from the person you are talking to, 
                                    an outsider who may possess the skills needed to unravel the mystery.""")
                                    ]

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
           #context = doc_chain(user_input)
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
            
    


if __name__ =='__main__':
    main ()


