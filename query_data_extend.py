from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.base import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer

from prompts import (CONDENSE_QUESTION_PROMPT,
                     QA_PROMPT)

from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from langchain.schema import Document
from typing import List
# from few_shot_prompts_template import ( FEW_SHOT_PROMPT_TEMPLATE )


async def aget_relevant_documents(self, query: str) -> List[Document]:
    return self.get_relevant_documents(query)


VectorStoreRetriever.aget_relevant_documents = aget_relevant_documents


def get_chain(
        vectorstore: VectorStore, question_handler, stream_handler, tracing: bool = False
) -> ConversationalRetrievalChain:
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])

    # if tracing:
    #     tracer = LangChainTracer()
    #     tracer.load_default_session()
    #     manager.add_handler(tracer)
    #     question_manager.add_handler(tracer)
    #     stream_manager.add_handler(tracer)

    question_gen_llm = ChatOpenAI(
        model_name='gpt-3.5-turbo',
        temperature=0,
        verbose=True,
        callback_manager=question_manager,
    )

    streaming_llm = ChatOpenAI(
        model_name='gpt-3.5-turbo',
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        temperature=0,
    )

    question_generator = LLMChain(llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager)
    doc_chain = load_qa_chain(streaming_llm, chain_type="stuff", prompt=QA_PROMPT, callback_manager=manager)

    chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        question_generator=question_generator,
        combine_docs_chain=doc_chain,
      
    )

    return chain
