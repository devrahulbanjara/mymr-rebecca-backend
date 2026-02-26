import boto3

from app.services.chat_service import ChatService
from app.services.config_service import ConfigService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService

from .config import settings

# Singleton instance of MemoryService
_memory_service_instance = None


def get_bedrock_agent_runtime_client():
    return boto3.client(
        "bedrock-agent-runtime", region_name=settings.AWS_DEFAULT_REGION
    )


def get_bedrock_runtime_client():
    return boto3.client("bedrock-runtime", region_name=settings.AWS_DEFAULT_REGION)


def get_config_service():
    return ConfigService()


def get_memory_service():
    """
    Get singleton instance of MemoryService.
    This ensures conversation history is maintained across requests.
    """
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService(max_exchanges=6)
    return _memory_service_instance


def get_llm_service():
    client = get_bedrock_runtime_client()
    return LLMService(bedrock_runtime=client)


def get_retrievekb_service():
    client = get_bedrock_agent_runtime_client()
    config_service = get_config_service()
    llm_service = get_llm_service()
    memory_service = get_memory_service()
    return ChatService(
        bedrock_agent_runtime=client,
        config_service=config_service,
        llm_service=llm_service,
        memory_service=memory_service,
    )
