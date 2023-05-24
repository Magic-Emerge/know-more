from typing import List

from langchain import OpenAI
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI

from langchain.schema import Document
from langchain.vectorstores.base import VectorStoreRetriever
from app.vectors.get_vectors import get_vector_store
from app.config.conf import DEFAULT_COLLECTION_NAME

from app.prompts.prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT


async def aget_relevant_documents(self, query: str) -> List[Document]:
    return self.get_relevant_documents(query)


VectorStoreRetriever.aget_relevant_documents = aget_relevant_documents


def get_chain(
        question_handler,
        stream_handler,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        model_name: str = "gpt-3.5-turbo", temperature: int = 0,
        chain_type: str = "stuff", question_prompt: str = CONDENSE_QUESTION_PROMPT,
        qa_prompt: str = QA_PROMPT
) -> ConversationalRetrievalChain:
    vector_store = get_vector_store(collection_name=collection_name)

    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])

    question_gen_llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        verbose=True,
        callback_manager=question_manager,
    )

    streaming_llm = ChatOpenAI(
        model_name=model_name,
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        temperature=temperature
    )

    question_generator = LLMChain(llm=question_gen_llm, prompt=question_prompt, callback_manager=manager)
    doc_chain = load_qa_chain(streaming_llm, chain_type=chain_type, prompt=qa_prompt, callback_manager=manager)

    # llm = OpenAI(temperature=0)
    # 使用上下文压缩改进文档检索
    # compressor = LLMChainExtractor.from_llm(llm)
    retriever = vector_store.as_retriever()
    # compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,
    #                                                        base_retriever=retriever)
    chain = ConversationalRetrievalChain(
        retriever=retriever,
        question_generator=question_generator,
        combine_docs_chain=doc_chain,

    )
    return chain
