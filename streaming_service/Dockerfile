FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY streaming_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/streaming_service
RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN python manage.py migrate
EXPOSE 8004
CMD ["gunicorn", "--bind", "0.0.0.0:8004", "streaming_project.wsgi:application"]
