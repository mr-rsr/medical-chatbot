from langchain.tools import tool
from backend.rag.faq_rag import search_faq

@tool
async def search_faq_tool(question: str) -> str:
    """
    Search the clinic FAQ and information database to answer patient questions.
    
    Args:
        question: The patient's question about clinic policies, procedures, or general information
    
    Returns:
        Answer from the clinic knowledge base
    """
    try:
        answer = await search_faq(question)
        return answer
    except Exception as e:
        return f"I apologize, but I couldn't find information about that. Please contact the clinic directly for assistance."
