FROM python:3.11.13-slim-bookworm@sha256:86adf8dbadc3d6e82ee5dd2c74bec2e1c2467cdad47886280501df722372d2e1 AS build
WORKDIR /build
COPY requirements-ci.txt pyproject.toml ./
COPY src ./src
RUN python -m pip wheel --wheel-dir /wheels -r requirements-ci.txt .

FROM python:3.11.13-slim-bookworm@sha256:86adf8dbadc3d6e82ee5dd2c74bec2e1c2467cdad47886280501df722372d2e1 AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build /wheels /wheels
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels quickcart-api && rm -rf /wheels
WORKDIR /app
COPY fixtures/synthetic-principals.json /app/principals.json
ENV QUICKCART_PRINCIPALS_FILE=/app/principals.json QUICKCART_TRIAGE_TIMEOUT_SECONDS=0.5
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=5 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)"]
CMD ["python", "-m", "uvicorn", "quickcart_api.app:create_app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "20", "--no-access-log"]
