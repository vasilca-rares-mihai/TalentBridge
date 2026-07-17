FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiaza requirements INAINTE de cod (profita de layer cache)
COPY service/analysis_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiaza codul sursa
COPY . .

CMD ["python", "-m", "celery", "-A", "service.analysis_worker.app.worker:celery_app", "worker", "--loglevel=info", "--pool=solo", "-c", "1"]