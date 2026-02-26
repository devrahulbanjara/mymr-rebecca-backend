from app.core.config import settings
from app.schemas.chat_schemas import (
    ChatRequest,
    ChatResponse,
    RetrievalResponse,
    RetrievalResult,
    LLMResponse,
)
from app.services.config_service import ConfigService
import time
from prompts import SYSTEM_PROMPT


class ChatService:
    def __init__(
        self, bedrock_agent_runtime, config_service: ConfigService, llm_service
    ) -> None:
        self.bedrock_agent_runtime = bedrock_agent_runtime
        self.config_service = config_service
        self.llm_service = llm_service

    def fetch_chunks(self, request: ChatRequest) -> RetrievalResponse:
        """
        Calls the Retrieve API and returns raw results without generation.
        """
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
        """
        Helper function to call the Bedrock Retrieve API.
        """
        vector_search_config = self.config_service.get_vector_search_config(
            request.patient_id, request.document_type
        )

        response = self.bedrock_agent_runtime.retrieve(
            knowledgeBaseId=settings.KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": request.query},
            retrievalConfiguration={"vectorSearchConfiguration": vector_search_config},
        )

        return response.get("retrievalResults", [])

    def generate_response(self, USER_QUESTION: str, CHUNKS: RetrievalResponse):
        user_content = (
            f"CONTEXT (Retrieved Medical Records/Knowledge):\n{CHUNKS}\n\n"
            f"USER QUESTION: {USER_QUESTION}\n\n"
            f"ASSISTANT TASK: Provide a concise, structured and meaningful response based on the context above."
        )

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_content}"

        # =========================
        # Claude
        # =========================

        PRICE_INPUT_PER_M = 3.00
        PRICE_OUTPUT_PER_M = 15.00

        start_claude = time.perf_counter()
        claude_raw, input_tokens, output_tokens = self.llm_service.infer_claude(
            full_prompt
        )
        end_claude = time.perf_counter()

        cost_input = (input_tokens / 1_000_000) * PRICE_INPUT_PER_M
        cost_output = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_M

        total_cost = cost_input + cost_output

        claude_obj = LLMResponse(
            model_name="Claude-3.5-Sonnet",
            response=claude_raw,
            latency=end_claude - start_claude,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=total_cost,
        )

        # =========================
        # Medgemma (COMMENTED OUT)
        # =========================
        """
        start_medgemma = time.perf_counter()
        medgemma_raw = self.llm_service.infer_medgemma(full_prompt)
        end_medgemma = time.perf_counter()
        medgemma_obj = LLMResponse(
            model_name="MedGemma-4B",
            response=medgemma_raw,
            latency=end_medgemma - start_medgemma,
        )
        """

        # Return only Claude in the list
        return ChatResponse(complete_response=[claude_obj])
