from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "GaiA-ABiz-Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth2
    OAUTH2_CLIENT_ID: str
    OAUTH2_CLIENT_SECRET: str
    OAUTH2_REDIRECT_URI: str

    # Encryption
    ENCRYPTION_KEY: str
    KEY_ROTATION_DAYS: int = 90

    # LLM Configuration (Local Only)
    LLM_PROVIDER: str = "local"
    LLM_MODEL_PATH: str = "scripts/models/qwen2.5-gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    LLM_CONTEXT_LENGTH: int = 32768
    LLM_N_THREADS: int = 8

    # Embeddings Configuration (Local Only)
    EMBEDDINGS_PROVIDER: str = "local"
    EMBEDDINGS_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDINGS_DIMENSION: int = 384

    # Milvus Vector Database
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "gaia_embeddings"

    # Monitoring
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Kubernetes
    KUBERNETES_NAMESPACE: str = "gaia-abiz"
    KUBERNETES_CONFIG_PATH: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
