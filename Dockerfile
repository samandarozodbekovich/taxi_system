# One image for the backend, the Celery worker and both Telegram bots (see docker-compose.yml)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# GDAL/GEOS/PROJ for GeoDjango (PostGIS)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gdal-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect admin static files for WhiteNoise. Settings require these values,
# so dummy ones are used at build time only - real ones come from backend/.env.
RUN cd backend && DJANGO_SECRET_KEY=build-only DB_PASSWORD=build-only \
    python manage.py collectstatic --noinput

WORKDIR /app/backend
EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
