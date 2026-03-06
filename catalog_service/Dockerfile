FROM python:3.11-slim

WORKDIR /app

COPY catalog_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR /app/catalog_service

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8002

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "catalog_project.wsgi:application"]
