FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# FOLOSIM "python -m uvicorn"
CMD ["python", "-m", "uvicorn", "service.core_service.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]