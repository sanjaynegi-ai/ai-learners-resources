FROM python:3.11.13-slim-bookworm@sha256:86adf8dbadc3d6e82ee5dd2c74bec2e1c2467cdad47886280501df722372d2e1
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY workbooks/capstone/merchant-support/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /app/requirements.txt
COPY workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/src /app/retrieval/src
COPY workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/secure-fixtures /app/retrieval/secure-fixtures
COPY workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/security-metadata.json /app/retrieval/security-metadata.json
COPY workbooks/capstone/merchant-support/src /app/src
ENV PYTHONPATH=/app/src:/app/retrieval/src CAPSTONE_RETRIEVAL=/app/retrieval CAPSTONE_STATE=/state
RUN mkdir /state && chown 10001:10001 /state
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=5 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)"]
CMD ["python", "-m", "uvicorn", "merchant_support.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "20", "--timeout-keep-alive", "2", "--no-access-log"]
