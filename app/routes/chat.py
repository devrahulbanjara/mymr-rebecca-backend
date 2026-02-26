from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_chat_service
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
):
    """The endpoint responsible for generating a response to a chat request."""
    return service.generate_response(request)
