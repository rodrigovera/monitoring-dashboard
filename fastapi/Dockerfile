FROM python:3.11-slim

# Crear usuario no root antes de trabajar
RUN useradd -ms /bin/bash appuser

WORKDIR /app

# Instalar curl y crear logs con permisos correctos
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cambiar a usuario seguro
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
