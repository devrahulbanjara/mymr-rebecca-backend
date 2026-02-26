from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    patient_id: str
    document_type: Optional[str] = None


class RetrievalResult(BaseModel):
    content: str
    score: float
    uri: Optional[str] = None


class RetrievalResponse(BaseModel):
    results: List[RetrievalResult]


class LLMResponse(BaseModel):
    model_name: str
    response: str
    latency: Optional[float] = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_cost: float | None = None
    kb_fetched: bool = False


class ChatResponse(BaseModel):
    complete_response: List[LLMResponse]
