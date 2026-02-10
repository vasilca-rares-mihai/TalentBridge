# Folosim o versiune ușoară de Python
FROM python:3.11-slim

# Setăm directorul de lucru
WORKDIR /app

# Instalăm dependențele de sistem necesare (de ex. pentru mysql client)
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Copiem fișierul de cerințe din rădăcina proiectului (vezi explicația din docker-compose)
COPY requirements.txt .

# Instalăm librăriile Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiem tot codul sursă în container
COPY . .

# Expunem portul
EXPOSE 8000

# FOLOSIM "python -m uvicorn" IN LOC DE "uvicorn"
CMD ["python", "-m", "uvicorn", "service.auth_service.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]