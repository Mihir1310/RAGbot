"""Application configuration loaded from environment variables / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAGBOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_model: str = "qwen2.5:3b"
    embed_model: str = "all-MiniLM-L6-v2"
    chroma_path: str = "./chroma_db"
    collection: str = "my_docs"
    data_dir: str = "./data"
    top_k: int = 4
    chunk_size: int = 400
    chunk_overlap: int = 50

# Changes 2
settings = Settings()
