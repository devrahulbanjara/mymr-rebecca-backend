from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    NUMBER_OF_CHUNKS_TO_FETCH: int = 20
    NUMBER_OF_RESULTS_AFTER_RERANKING: int = 5
    MODEL_ID: str
    RERANK_MODEL_ARN: str
    AWS_DEFAULT_REGION: str
    KNOWLEDGE_BASE_ID: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
