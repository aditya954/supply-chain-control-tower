# AI Supply Chain Inventory Risk Assistant
FROM python:3.11-slim

LABEL maintainer="supply-chain-team"
LABEL description="Snowflake + dbt + RAG supply chain risk assistant"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DBT_PROFILES_DIR=/app

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --gid 10001 appgroup \
    && useradd --uid 10001 --gid appgroup --create-home appuser

# Python dependencies (no secrets in image)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Application code
COPY dbt_project.yml profiles.yml packages.yml package-lock.yml pytest.ini ./
COPY macros/ macros/
COPY models/ models/
COPY src/ src/
COPY scripts/ scripts/
COPY snowflake/ snowflake/
COPY data/inventory_risk/ data/inventory_risk/
COPY tests/ tests/

RUN chown -R appuser:appgroup /app
USER appuser

# Runtime configuration via environment variables / mounted secrets
# Required at run time:
#   SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_PATH (mount key file)
#   SNOWFLAKE_PRIVATE_KEY_PASSPHRASE, LLM_API_KEY (or LLM_PROVIDER=cortex)

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import src.application.cli; import src.ai.rag" || exit 1

ENTRYPOINT ["python", "-m", "src.application.cli"]
CMD []
