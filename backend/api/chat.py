from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse
from backend.agent.scheduling_agent import agent_instance

router = APIRouter()

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = await agent_instance.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=result["response"],
            booking_details=result.get("booking_details"),
            action_performed=result.get("action_performed")
        )
    
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        
        if "ThrottlingException" in str(e) or "Too many requests" in str(e):
            return ChatResponse(
                response="I'm experiencing high demand right now. Please wait a moment and try again.",
                booking_details=None,
                action_performed=None
            )
        
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
