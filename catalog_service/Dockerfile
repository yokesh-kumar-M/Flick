FROM python:3.11-slim AS builder
WORKDIR /app
COPY catalog_service/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/catalog_service
RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN python manage.py migrate
RUN python manage.py seed_catalog

EXPOSE 8002

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--timeout", "120", "--keep-alive", "5", "catalog_project.wsgi:application"]