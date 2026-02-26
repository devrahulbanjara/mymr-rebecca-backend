import boto3

from app.services.chat_service import ChatService
from app.services.config_service import ConfigService

from . import settings


def get_bedrock_client():
    return boto3.client(
        "bedrock-agent-runtime", region_name=settings.AWS_DEFAULT_REGION
    )


def get_config_service():
    return ConfigService()


def get_chat_service():
    client = get_bedrock_client()
    config_service = get_config_service()
    return ChatService(bedrock_client=client, config_service=config_service)
