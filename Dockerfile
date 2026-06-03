FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir duckdb requests "soda-core<4" "soda-core-duckdb==3.5.6"

COPY . /app

CMD ["python", "pipeline.py"]