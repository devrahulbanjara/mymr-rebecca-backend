from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    patient_id: str
    document_type: Optional[str] = None


class UsefulCitation(BaseModel):
    start_character: int
    end_character: int
    source_chunk: str
    file_uri: str
    page_number: int


class ChatResponse(BaseModel):
    answer: str
    useful_citations: list[UsefulCitation]
