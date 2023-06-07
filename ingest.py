#Code by Langchain

# """Load html from files, clean up, split, ingest into Weaviate."""
# import pickle

# from langchain.document_loaders import ReadTheDocsLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores.faiss import FAISS


# def ingest_docs():
#     """Get documents from web pages."""
#     loader = ReadTheDocsLoader("langchain.readthedocs.io/en/latest/")
#     raw_documents = loader.load()
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#     )
#     documents = text_splitter.split_documents(raw_documents)
#     embeddings = OpenAIEmbeddings()
#     vectorstore = FAISS.from_documents(documents, embeddings)

#     # Save vectorstore
#     with open("vectorstore.pkl", "wb") as f:
#         pickle.dump(vectorstore, f)


# if __name__ == "__main__":
#     ingest_docs()


#Modified code for us
"""Load PDF from files, clean up, split, ingest into Weaviate."""
import os
import pickle
from pathlib import Path
import textract

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.environ['OPENAI_API_KEY']

def clean_data(data):
    # You can add any PDF cleanup code here if needed
    return data

def ingest_docs():
    """Get documents from local PDF files."""
    docs = []
    metadatas = []
    for p in Path("/Users/yellow/Documents/Code/Alcade/Alcade/Alcade/Story/").rglob("*"):
        if p.is_dir() or not str(p).endswith('.pdf'):
            continue
        data = textract.process(str(p)).decode('utf-8')  # Decode bytes to string
        docs.append(clean_data(data))
        metadatas.append({"source": p})

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.create_documents(docs, metadatas=metadatas)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()
