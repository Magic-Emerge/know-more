"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle
import os

from langchain.document_loaders import ReadTheDocsLoader, UnstructuredFileLoader, TextLoader, UnstructuredHTMLLoader, \
    UnstructuredPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from milvus import Milvus

os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""

MILVUS_CONNECTION_ARGS = {
    "host": "10.39.201.210",
    "port": "30530",
}
MILVUS_COLLECTION_NAME = 'badcase_default'
MILVUS_TEXT_FIELD = 'badcase_text_field_default'

def ingest_badcase_txt_2_milvus():
    """Get documents from web pages."""
    loader = UnstructuredHTMLLoader("./assets/templates/badcase.txt", encoding='UTF-8')
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    Milvus.from_documents(documents, embeddings,
                                        connection_args=MILVUS_CONNECTION_ARGS,
                                        collection_name=MILVUS_COLLECTION_NAME,
                                        text_field=MILVUS_TEXT_FIELD)


def ingest_docs_2_milvus():
    """Get documents from web pages."""
    loader = UnstructuredHTMLLoader("../../files/html/廊坊热水器开通业务.html", encoding='UTF-8')
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = Milvus.from_documents(documents, embeddings,
                                        connection_args=MILVUS_CONNECTION_ARGS,
                                        collection_name=MILVUS_COLLECTION_NAME,
                                        text_field=MILVUS_TEXT_FIELD)

    # Save vectorstore
    # with open("vectorstore.pkl", "wb") as f:
    #     pickle.dump(vectorstore, f)


def ingest_pdf_2_milvus():
    """Get documents from pdf files."""
    loader = UnstructuredPDFLoader("../../files/城镇燃气调压器(GB27790-2020).pdf")
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = Milvus.from_documents(documents, embeddings,
                                        connection_args=MILVUS_CONNECTION_ARGS,
                                        collection_name=MILVUS_COLLECTION_NAME,
                                        text_field=MILVUS_TEXT_FIELD)

    # Save vectorstore
    # with open("vectorstore.pkl", "wb") as f:
    #     pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_badcase_txt_2_milvus()

