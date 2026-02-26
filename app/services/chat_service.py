from app.core.config import settings
from app.schemas.chat_schemas import (
    ChatRequest,
    ChatResponse,
    RetrievalResponse,
    RetrievalResult,
    LLMResponse,
)
from app.services.config_service import ConfigService
from app.services.memory_service import MemoryService
import time
from prompts import SYSTEM_PROMPT


class ChatService:
    def __init__(
        self,
        bedrock_agent_runtime,
        config_service: ConfigService,
        llm_service,
        memory_service: MemoryService,
    ) -> None:
        self.bedrock_agent_runtime = bedrock_agent_runtime
        self.config_service = config_service
        self.llm_service = llm_service
        self.memory_service = memory_service

    def fetch_chunks(self, request: ChatRequest) -> RetrievalResponse:
        retrieval_results = self._retrieve_only(request)
        formatted_results = []
        for result in retrieval_results:
            content_text = result.get("content", {}).get("text", "")
            score = result.get("score", 0.0)
            uri = result.get("location", {}).get("s3Location", {}).get("uri")
            formatted_results.append(
                RetrievalResult(content=content_text, score=score, uri=uri)
            )
        return RetrievalResponse(results=formatted_results)

    def _retrieve_only(self, request: ChatRequest):
        vector_search_config = self.config_service.get_vector_search_config(
            request.patient_id, request.document_type
        )
        response = self.bedrock_agent_runtime.retrieve(
            knowledgeBaseId=settings.KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": request.query},
            retrievalConfiguration={"vectorSearchConfiguration": vector_search_config},
        )
        return response.get("retrievalResults", [])

    def generate_response(self, USER_QUESTION: str, patient_id: str, request: ChatRequest):
        # 1. Get conversation history BEFORE adding the current message
        conversation_history = self.memory_service.get_conversation_history(patient_id)
        history_str = self.memory_service.get_formatted_history(patient_id)

        # 2. Classify intent
        kb_required = self.llm_service.classify_intent(USER_QUESTION, history_str)

        # 3. Build user turn prompt
        if kb_required:
            chunks = self.fetch_chunks(request)
            context_data = "\n".join([f"- {c.content}" for c in chunks.results])
            user_turn_prompt = (
                f"NEWLY RETRIEVED MEDICAL RECORDS:\n{context_data}\n\n"
                f"USER QUESTION: {USER_QUESTION}"
            )
        else:
            # No KB needed — just ask the question. Claude already has the
            # conversation history in the multi-turn message thread.
            user_turn_prompt = f"USER QUESTION: {USER_QUESTION}"

        # 4. Call Claude
        PRICE_INPUT_PER_M = 3.00
        PRICE_OUTPUT_PER_M = 15.00

        start_claude = time.perf_counter()
        claude_raw, input_tokens, output_tokens = self.llm_service.infer_claude(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_turn_prompt,
            conversation_history=conversation_history,
        )
        end_claude = time.perf_counter()

        total_cost = (input_tokens / 1_000_000) * PRICE_INPUT_PER_M + \
                     (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_M

        claude_obj = LLMResponse(
            model_name="Claude-3.5-Sonnet",
            response=claude_raw,
            latency=end_claude - start_claude,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=total_cost,
            kb_fetched=kb_required,
        )

        # 5. Store exchange in memory AFTER the response
        self.memory_service.add_message(patient_id, "user", USER_QUESTION)
        self.memory_service.add_message(patient_id, "assistant", claude_raw)

        return ChatResponse(complete_response=[claude_obj])