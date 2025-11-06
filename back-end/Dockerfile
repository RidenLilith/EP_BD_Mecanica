# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps básicos (psycopg2-binary dispensa libpq-dev, então é leve)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# roda o seed na primeira subida (idempotente)
CMD [ "bash", "-lc", "python app.py & sleep 2 && python seed.py && wait -n" ]
