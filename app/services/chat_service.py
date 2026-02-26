from app.schemas import ChatRequest, ChatResponse, UsefulCitation
from app.services.config_service import ConfigService


class ChatService:
    def __init__(self, bedrock_client, config_service: ConfigService) -> None:
        self.bedrock_agent_runtime = bedrock_client
        self.config_service = config_service

    def generate_response(self, request: ChatRequest) -> ChatResponse:
        """The main service function that calls other helper private functions to generate and send response back to the endpoint."""
        response, citations = self._retrieve_and_generate(request)

        useful_citations = self._extract_useful_citations(citations)

        return ChatResponse(
            answer=response,
            useful_citations=useful_citations,
        )

    def _extract_useful_citations(self, citations: list) -> list[UsefulCitation]:
        """The function responsible for extracting useful citations from the complete retrieved citations."""
        useful_citations = []

        for source in citations:
            start_character = source["generatedResponsePart"]["textResponsePart"][
                "span"
            ]["start"]
            end_character = source["generatedResponsePart"]["textResponsePart"]["span"][
                "end"
            ]

            try:
                for ref in source["retrievedReferences"]:
                    source_chunk = ref["content"]["text"]
                    file_uri = ref["location"]["s3Location"]["uri"]
                    page_num = ref["metadata"].get(
                        "x-amz-bedrock-kb-document-page-number"
                    )

                    useful_citations.append(
                        UsefulCitation(
                            source_chunk=source_chunk,
                            file_uri=file_uri,
                            page_number=page_num,
                            start_character=start_character,
                            end_character=end_character,
                        )
                    )
            except Exception as e:
                print(f"Error processing citation: {e}")

        return useful_citations

    def _retrieve_and_generate(self, request: ChatRequest):
        """The helper function responsible to fetch a config and using that config, generate an answer and send back to the main response generator service function"""
        config = self.config_service.get_retrieval_config(
            request.patient_id, request.document_type
        )

        response = self.bedrock_agent_runtime.retrieve_and_generate(
            input={"text": request.query},
            retrieveAndGenerateConfiguration=config,
        )

        return response["output"]["text"], response["citations"]
