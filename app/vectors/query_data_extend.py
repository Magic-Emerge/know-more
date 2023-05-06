from typing import List

from langchain.callbacks.manager import AsyncCallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever

from app.prompts.prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT


async def aget_relevant_documents(self, query: str) -> List[Document]:
    return self.get_relevant_documents(query)


VectorStoreRetriever.aget_relevant_documents = aget_relevant_documents


def get_chain(
        vectorstore: VectorStore, question_handler, stream_handler,
        model_name: str = "gpt-3.5-turbo", temperature: int = 0
) -> ConversationalRetrievalChain:
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

    question_generator = LLMChain(llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager)
    doc_chain = load_qa_chain(streaming_llm, chain_type="stuff", prompt=QA_PROMPT, callback_manager=manager)

    chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        question_generator=question_generator,
        combine_docs_chain=doc_chain,

    )
    return chain
