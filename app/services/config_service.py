from typing import Optional

from app.core import settings
from prompts import GENERATION_PROMPT, ORCHESTRATION_PROMPT


class ConfigService:
    def __init__(self):
        pass

    def _get_filters(self, patient_id: str, document_type: Optional[str] = None):
        """This function is responsible for creating filters based on patient_id and document_type if provided in the request or not."""
        if document_type:
            return {
                "andAll": [
                    {
                        "equals": {
                            "key": "patient_id",
                            "value": patient_id,
                        }
                    },
                    {
                        "equals": {
                            "key": "document_type",
                            "value": document_type,
                        }
                    },
                ]
            }
        return {"equals": {"key": "patient_id", "value": patient_id}}

    def get_retrieval_config(
        self, patient_id: str, document_type: Optional[str] = None
    ):
        """The function responsible for fetching filters, and adjusting config so that the chat_service class could use it"""
        filter = self._get_filters(patient_id, document_type)
        return {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": settings.KNOWLEDGE_BASE_ID,
                "modelArn": settings.MODEL_ARN,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": settings.NUMBER_OF_CHUNKS_TO_FETCH,
                        "filter": filter,
                        "rerankingConfiguration": {
                            "type": "BEDROCK_RERANKING_MODEL",
                            "bedrockRerankingConfiguration": {
                                "modelConfiguration": {
                                    "modelArn": settings.RERANK_MODEL_ARN
                                },
                                "numberOfRerankedResults": settings.NUMBER_OF_RESULTS_AFTER_RERANKING,
                            },
                        },
                    }
                },
                "generationConfiguration": {
                    "promptTemplate": {
                        "textPromptTemplate": GENERATION_PROMPT,
                    },
                    "inferenceConfig": {
                        "textInferenceConfig": {
                            "temperature": 0.1,
                            "topP": 0.5,
                            "maxTokens": 2048,
                            "stopSequences": ["\nObservation"],
                        }
                    },
                },
                "orchestrationConfiguration": {
                    "queryTransformationConfiguration": {"type": "QUERY_DECOMPOSITION"},
                    "promptTemplate": {
                        "textPromptTemplate": ORCHESTRATION_PROMPT,
                    },
                    "inferenceConfig": {
                        "textInferenceConfig": {
                            "temperature": 0.2,
                            "maxTokens": 2048,
                            "stopSequences": ["\nObservation"],
                        }
                    },
                },
            },
        }
