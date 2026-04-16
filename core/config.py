from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'cbn-rag-demo'
    app_env: str = 'development'
    api_prefix: str = '/api'

    jwt_secret_key: str = Field(default='change-me')
    access_token_expire_minutes: int = 120
    jwt_algorithm: str

    database_url: str
    openai_api_key: str
    chat_model: str = 'gpt-4o-mini'
    embedding_model: str = 'text-embedding-3-small'
    embedding_dimension: int = 1536

    langfuse_secret_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_host: str = 'https://us.cloud.langfuse.com'

    blob_connection_string: str | None = None
    blob_container: str = 'testing'


settings = Settings()
