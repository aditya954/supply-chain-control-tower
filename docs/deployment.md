# Deployment Guide

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env          # fill Snowflake + LLM credentials
export DBT_PROFILES_DIR=$(pwd)

python3 scripts/load_inventory_risk_to_snowflake.py
dbt build --select inventory_risk
python -m src.ai.embeddings
python -m src.application.cli -q "Which products are at critical risk?"
```

## Docker

### Build

```bash
docker build -t inventory-risk-assistant:latest .
```

### Run (interactive)

```bash
docker run -it --rm \
  --env-file .env \
  -e SNOWFLAKE_PRIVATE_KEY_PATH=/secrets/rsa_key.p8 \
  -v /path/to/rsa_key.p8:/secrets/rsa_key.p8:ro \
  inventory-risk-assistant:latest
```

### Run (single question)

```bash
docker run --rm \
  --env-file .env \
  -e SNOWFLAKE_PRIVATE_KEY_PATH=/secrets/rsa_key.p8 \
  -v /path/to/rsa_key.p8:/secrets/rsa_key.p8:ro \
  inventory-risk-assistant:latest \
  -q "Why is Coconut Body Wash at risk?"
```

> Never bake credentials into the image. Mount keys and pass secrets at runtime.

## GitHub Actions CI/CD

Pipeline: `lint` → `unit_test` → `dbt_compile` → `dbt_test` → `ai_test` → `docker_build`

Workflow file: `.github/workflows/ci.yml`

### Required GitHub secrets (Settings → Secrets and variables → Actions)

| Secret | Purpose |
|--------|---------|
| `SNOWFLAKE_ACCOUNT` | dbt build / integration tests |
| `SNOWFLAKE_USER` | dbt build / integration tests |
| `SNOWFLAKE_PRIVATE_KEY` | Base64-encoded `.p8` key file |
| `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE` | Key passphrase |
| `SNOWFLAKE_ROLE` | Optional (default `TRANSFORMER`) |
| `SNOWFLAKE_WAREHOUSE` | Optional (default `DBT_WH`) |
| `SNOWFLAKE_DATABASE` | Optional (default `ANALYTICS`) |

### Repository variable

| Variable | Value | Purpose |
|----------|-------|---------|
| `ENABLE_SNOWFLAKE_CI` | `true` | Enables Snowflake dbt build + integration test jobs |

Snowflake-dependent jobs run when `ENABLE_SNOWFLAKE_CI=true`.

### Encode your Snowflake key for GitHub

```bash
base64 -i ~/.dbt/snowflake_keys/rsa_key.p8 | pbcopy
# Paste into GitHub secret SNOWFLAKE_PRIVATE_KEY
```

### Push to GitHub

```bash
git remote -v   # should point to github.com
git push origin dev
```

Actions run on push/PR to `main` and `dev`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Insufficient data.` | Run embeddings sync; verify `IR_DOCUMENT_EMBEDDINGS` has rows |
| dbt test fails on relationships | Reload RAW data: `load_inventory_risk_to_snowflake.py` |
| Cortex embedding error | Check Cortex enabled on account; or set `EMBEDDING_PROVIDER=local` |
| LLM timeout | Increase `LLM_TIMEOUT_SECONDS` in `.env` |
