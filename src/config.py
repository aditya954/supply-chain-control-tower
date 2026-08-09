"""Application configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str
    role: str
    warehouse: str
    database: str
    private_key_path: str
    private_key_passphrase: str


@dataclass(frozen=True)
class EmbeddingConfig:
    provider: str
    model: str
    version: str
    dimension: int
    context_table: str
    embeddings_table: str
    search_table: str


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: int
    max_retries: int


@dataclass(frozen=True)
class AppConfig:
    snowflake: SnowflakeConfig
    embedding: EmbeddingConfig
    llm: LLMConfig


def load_config() -> AppConfig:
    load_dotenv(PROJECT_ROOT / ".env")

    snowflake = SnowflakeConfig(
        account=os.environ.get("SNOWFLAKE_ACCOUNT", ""),
        user=os.environ.get("SNOWFLAKE_USER", ""),
        role=os.environ.get("SNOWFLAKE_ROLE", "TRANSFORMER"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "DBT_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS"),
        private_key_path=os.environ.get(
            "SNOWFLAKE_PRIVATE_KEY_PATH",
            str(Path.home() / ".dbt/snowflake_keys/rsa_key.p8"),
        ),
        private_key_passphrase=os.environ.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", ""),
    )

    provider = os.environ.get("EMBEDDING_PROVIDER", "cortex").lower()
    model = os.environ.get(
        "EMBEDDING_MODEL",
        "snowflake-arctic-embed-m" if provider == "cortex" else "all-MiniLM-L6-v2",
    )
    dimension = int(os.environ.get("EMBEDDING_DIMENSION", "768" if provider == "cortex" else "384"))

    embedding = EmbeddingConfig(
        provider=provider,
        model=model,
        version=os.environ.get("EMBEDDING_VERSION", "v1"),
        dimension=dimension,
        context_table=os.environ.get(
            "AI_CONTEXT_TABLE", "AI_IR_SUPPLY_CHAIN_CONTEXT"
        ).upper(),
        embeddings_table=os.environ.get(
            "AI_EMBEDDINGS_TABLE", "IR_DOCUMENT_EMBEDDINGS"
        ).upper(),
        search_table=os.environ.get(
            "AI_SEARCH_TABLE", "IR_DOCUMENT_EMBEDDINGS_SEARCH"
        ).upper(),
    )

    llm_provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    default_llm_model = (
        "mistral-large2" if llm_provider == "cortex" else "gpt-4o-mini"
    )
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

    llm = LLMConfig(
        provider=llm_provider,
        model=os.environ.get("LLM_MODEL", default_llm_model),
        api_key=api_key,
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        timeout_seconds=int(os.environ.get("LLM_TIMEOUT_SECONDS", "60")),
        max_retries=int(os.environ.get("LLM_MAX_RETRIES", "3")),
    )

    return AppConfig(snowflake=snowflake, embedding=embedding, llm=llm)
