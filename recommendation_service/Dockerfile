FROM python:3.11-slim AS builder
WORKDIR /app
COPY recommendation_service/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/recommendation_service
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8005

CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:${PORT:-8000} recommendation_project.wsgi:application"]

