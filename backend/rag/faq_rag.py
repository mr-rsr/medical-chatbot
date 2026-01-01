from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from backend.rag.vector_store import get_vector_store
import os

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def create_rag_chain():
    llm = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_kwargs={"temperature": 0.7, "max_tokens": 2000}
    )
    
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    template = """You are a helpful medical clinic assistant. Use the following context to answer the question.
If you cannot find the answer in the context, say so politely.

Context:
{context}

Question: {question}

Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

async def search_faq(question: str) -> str:
    rag_chain = create_rag_chain()
    result = await rag_chain.ainvoke(question)
    return result
