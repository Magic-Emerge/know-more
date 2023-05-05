"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle
import os

from langchain.document_loaders import ReadTheDocsLoader, UnstructuredFileLoader, TextLoader, UnstructuredHTMLLoader, \
    UnstructuredPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from milvus import Milvus

os.environ["OPENAI_API_BASE"] = "http://10.8.0.12:8888/api/v1"
os.environ["OPENAI_API_KEY"] = "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"


MILVUS_CONNECTION_ARGS = {
    "host": "10.39.201.210",
    "port": "30530",
}
MILVUS_COLLECTION_NAME = 'badcase_default'
MILVUS_TEXT_FIELD = 'badcase_text_field_default'



def ingest_pdf_2_milvus(
        file_path: str,
        collection_name: str,
        text_field: str,
        chunk_size=2000,
        chunk_overlap=200,
):
    """
    Get documents from pdf files.
    :param file_path 文件路径
    :param collection_name milvus collection
    :param text_field milvus文本字段名称
    :param chunk_size 文本切分大小，默认2000
    :param chunk_overlap 切分重叠大小，默认200
    """
    loader = UnstructuredFileLoader(file_path)
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    if Milvus.exist_collection(connection_args=MILVUS_CONNECTION_ARGS, collection_name=collection_name):
        milvus = Milvus.from_existing(embedding=embeddings, connection_args=MILVUS_CONNECTION_ARGS,
                                      collection_name=collection_name, text_field=text_field)
        milvus.add_documents(documents)
    else:
        vectorstore = Milvus.from_documents(documents, embeddings,
                                            connection_args=MILVUS_CONNECTION_ARGS,
                                            collection_name=collection_name,
                                            text_field=text_field)





def ingest_badcase_txt_2_milvus():
    """Get documents from web pages."""
    loader = UnstructuredHTMLLoader("../../assets/templates/badcase.txt", encoding='UTF-8')
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()

    if Milvus.exist_collection(connection_args=MILVUS_CONNECTION_ARGS, collection_name=MILVUS_COLLECTION_NAME):
        milvus = Milvus.from_existing(embedding=embeddings, connection_args=MILVUS_CONNECTION_ARGS,
                                      collection_name=MILVUS_COLLECTION_NAME, text_field=MILVUS_TEXT_FIELD)
        milvus.add_documents(documents)
    else:
        vectorstore = Milvus.from_documents(documents, embeddings,
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

