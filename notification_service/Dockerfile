FROM python:3.11-slim
WORKDIR /app
COPY notification_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/notification_service
RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN python manage.py migrate
EXPOSE 8006
CMD ["gunicorn", "--bind", "0.0.0.0:8006", "notification_project.wsgi:application"]
