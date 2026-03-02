from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: str = Field("3306", alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")

    secret_key: str = Field(..., alias="SECRET_KEY")
    kakao_client_id: str | None = Field(None, alias="KAKAO_CLIENT_ID")
    kakao_client_secret: str | None = Field(None, alias="KAKAO_CLIENT_SECRET")
    kakao_redirect_uri: str | None = Field(None, alias="KAKAO_REDIRECT_URI")
    gemini_api_key: str | None = Field(None, alias="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-1.5-flash", alias="GEMINI_MODEL")
    gemini_embed_model: str = Field("gemini-embedding-001", alias="GEMINI_EMBED_MODEL")
    rag_top_k: int = Field(4, alias="RAG_TOP_K")
    google_safe_browsing_api_key: str | None = Field(None, alias="GOOGLE_SAFE_BROWSING_API_KEY")
    ml_switch_threshold: int = Field(1000, alias="ML_SWITCH_THRESHOLD")
    url_model_path: str | None = Field(None, alias="URL_MODEL_PATH")
    bert_model_path: str | None = Field(None, alias="BERT_MODEL_PATH")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="allow",
        populate_by_name=True,
        case_sensitive=True,
    )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
