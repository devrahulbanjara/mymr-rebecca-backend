from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_retrievekb_service
from app.schemas import ChatRequest
from app.schemas.chat_schemas import ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_retrievekb_service)],
):
    """The endpoint responsible for generating a response to a chat request."""
    chunks = service.fetch_chunks(request)
    response = service.generate_response(request.query, chunks)
    return response
