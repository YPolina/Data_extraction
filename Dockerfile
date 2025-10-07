FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY run_pipeline.sh .
COPY data/ ./data/

ENV PYTHONPATH=/app

CMD ["./run_pipeline.sh"]
