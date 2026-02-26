from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from app.core.logging_config import logger
from app.core.dependencies import get_retrievekb_service, get_memory_service
from app.schemas import ChatRequest
from app.schemas.chat_schemas import ChatResponse, LLMResponse
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_retrievekb_service)],
):
    """The endpoint responsible for generating a response to a chat request."""
    try:
        response = service.generate_response(request.query, request.patient_id, request)
        return response
    except Exception as e:
        logger.error(f"Chat endpoint error | Patient: {request.patient_id} | Query: '{request.query[:100]}' | Error: {str(e)}")
        
        error_response = LLMResponse(
            model_name="Rebecca (Error Handler)",
            response=(
                "I apologize, but I'm experiencing some technical difficulties right now. "
                "This could be due to a temporary service interruption or connectivity issue.\n\n"
                "**What you can try:**\n"
                "- Wait a moment and try your question again\n"
                "- Rephrase your question if it was very complex\n"
                "- Check that your internet connection is stable\n\n"
                "If the problem persists, please contact your system administrator. "
                "I'm here to help as soon as the issue is resolved!"
            ),
            latency=0.0,
            input_tokens=0,
            output_tokens=0,
            total_cost=0.0,
            kb_fetched=False
        )
        
        return ChatResponse(complete_response=[error_response])


@router.get("/chat/history/{patient_id}")
async def get_chat_history(
    patient_id: str,
    memory_service: Annotated[MemoryService, Depends(get_memory_service)],
):
    """Get conversation history for a specific patient."""
    history = memory_service.get_conversation_history(patient_id)
    return {
        "patient_id": patient_id,
        "message_count": len(history),
        "exchange_count": len(history) // 2,
        "history": history
    }


@router.delete("/chat/history/{patient_id}")
async def clear_chat_history(
    patient_id: str,
    memory_service: Annotated[MemoryService, Depends(get_memory_service)],
):
    """Clear conversation history for a specific patient."""
    success = memory_service.clear_conversation_history(patient_id)
    return {
        "patient_id": patient_id,
        "cleared": success,
        "message": "Chat history cleared successfully" if success else "Failed to clear chat history"
    }


@router.get("/chat/stats")
async def get_memory_stats(
    memory_service: Annotated[MemoryService, Depends(get_memory_service)],
):
    """Get statistics about stored conversation histories."""
    stats = memory_service.get_stats()
    return stats
