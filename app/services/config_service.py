from typing import Optional

from app.core import settings


class ConfigService:
    def __init__(self):
        pass

    def _get_filters(self, patient_id: str, document_type: Optional[str] = None):
        """Creates filters based on patient_id and document_type."""
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

    def get_vector_search_config(
        self, patient_id: str, document_type: Optional[str] = None
    ):
        """
        Returns the vectorSearchConfiguration for the retrieve API.
        """
        filter_config = self._get_filters(patient_id, document_type)

        return {
            "numberOfResults": settings.NUMBER_OF_CHUNKS_TO_FETCH,
            "filter": filter_config,
            "rerankingConfiguration": {
                "type": "BEDROCK_RERANKING_MODEL",
                "bedrockRerankingConfiguration": {
                    "modelConfiguration": {"modelArn": settings.RERANK_MODEL_ARN},
                    "numberOfRerankedResults": settings.NUMBER_OF_RESULTS_AFTER_RERANKING,
                },
            },
        }
