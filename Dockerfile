FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.lock.txt /app/requirements.lock.txt
RUN python -m pip install --upgrade pip &&     python -m pip install -r /app/requirements.lock.txt

COPY . /app

CMD ["python", "src/run_benchmark.py", "--output-dir", "artifacts/docker-run"]
