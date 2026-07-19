FROM python:3.11-slim

# LibreOffice + polices courantes (essentielles pour un rendu fidèle)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    fonts-liberation fonts-dejavu-core fonts-noto-core \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 180 --workers 2 app:app
