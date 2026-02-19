FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "celery", "-A", "service.analysis_worker.app.worker:celery_app", "worker", "--loglevel=info", "--pool=solo", "-c", "1"]