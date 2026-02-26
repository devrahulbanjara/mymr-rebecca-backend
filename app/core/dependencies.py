import boto3

from app.services.chat_service import ChatService
from app.services.config_service import ConfigService
from app.services.llm_service import LLMService

from .config import settings


def get_bedrock_agent_runtime_client():
    return boto3.client(
        "bedrock-agent-runtime", region_name=settings.AWS_DEFAULT_REGION
    )


def get_bedrock_runtime_client():
    return boto3.client("bedrock-runtime", region_name=settings.AWS_DEFAULT_REGION)


def get_config_service():
    return ConfigService()


def get_retrievekb_service():
    client = get_bedrock_agent_runtime_client()
    config_service = get_config_service()
    llm_service = get_chat_service()
    return ChatService(
        bedrock_agent_runtime=client,
        config_service=config_service,
        llm_service=llm_service,
    )


def get_chat_service():
    client = get_bedrock_runtime_client()
    return LLMService(bedrock_runtime=client)
