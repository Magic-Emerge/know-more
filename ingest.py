"""Load html from files, clean up, split, ingest into Weaviate."""
import os
import pickle

from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""


def ingest_docs():
    """Get documents from web pages."""
    loader = UnstructuredFileLoader("assets/templates/badcase.txt")
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings(
    )
    

    # 替换成es
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()