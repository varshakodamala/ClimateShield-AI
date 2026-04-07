# Run Setup Checklist

This checklist explains what information must be present in key files so the Weather Dashboard project can run successfully.

## 1) Required dependency file

### `requirements.txt`
Keep all runtime libraries used by API, dashboard, pipeline, database, and cloud loaders:
- API/server: `fastapi`, `uvicorn`, `pydantic`
- Data: `pandas`, `numpy`, `requests`
- Storage: `sqlalchemy`, `psycopg2-binary`, `boto3`
- Config/env: `pyyaml`, `python-dotenv`
- UI/testing: `streamlit`, `pytest`
- Optional orchestration: `apache-airflow`, `docker`

If you remove packages used in code imports, runtime will fail.

## 2) Required runtime config files

### `config/settings.yaml`
Keep these sections and keys populated (or resolvable via environment variables):
- `weather_api.base_url`
- `weather_api.api_key` (via `${OPENWEATHER_API_KEY}`)
- `weather_api.units`
- `database.host`, `database.port`, `database.name`, `database.user`, `database.password`
- `aws.s3_bucket`, `aws.region`, `aws.access_key`, `aws.secret_key`
- `logging.level`, `logging.file`
- `alerts.email`, `alerts.smtp_server`, `alerts.smtp_port`, `alerts.smtp_user`, `alerts.smtp_password`

### `config/cities.yaml`
Keep at least one city entry with:
- `name`
- `country`
- `lat`
- `lon`

> Note: current pipeline code reads `cities` from `settings.yaml`, not `cities.yaml`. You must either:
> - pass `--cities ...` when running pipelines, or
> - add a `cities:` list directly in `settings.yaml`.

## 3) Required entrypoint and service files

### `main.py`
Keep command interface working for:
- `pipeline`
- `api`
- `dashboard`
- `validate`

### `services/api/main.py`
Keep API app creation, CORS middleware, route registration, and config loading.

### `services/dashboard/streamlit_app.py`
Keep the Streamlit app as the dashboard entrypoint.

## 4) Docker files (if using containers)

### `docker/docker-compose.yml`
Keep service definitions and environment variable pass-through for:
- `OPENWEATHER_API_KEY`
- `DB_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SMTP_USER`
- `SMTP_PASSWORD`

### `docker/Dockerfile`
Keep:
- Python base image
- `requirements.txt` install step
- project copy step
- default command for API startup

## 5) Environment variables you should provide

Create a `.env` file at project root (or export vars in shell):
- `OPENWEATHER_API_KEY`
- `DB_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SMTP_USER`
- `SMTP_PASSWORD`

Optional API runtime vars used by service startup:
- `API_HOST`
- `API_PORT`
- `API_RELOAD`

## 6) Existing consistency issues to be aware of

- `core/load/s3_loader.py` expects config section `s3`, but `settings.yaml` currently uses `aws`.
  - To make S3 loading work, either rename to `s3` in config or update loader code.
- `services/api/routes/weather_routes.py` uses `os.path.expandvars(...)` but does not import `os`.
  - Add `import os` to avoid route module load failure.

## 7) Minimal run order

1. Install dependencies: `pip install -r requirements.txt`
2. Provide required environment variables
3. Run API: `python main.py api`
4. Run Dashboard: `python main.py dashboard`
5. Run pipeline with explicit city list if needed:
   - `python main.py pipeline --cities "New York" "London"`
