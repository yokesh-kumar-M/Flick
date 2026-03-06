FROM python:3.11-slim
WORKDIR /app
COPY recommendation_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/recommendation_service
RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN python manage.py migrate
EXPOSE 8005
CMD ["gunicorn", "--bind", "0.0.0.0:8005", "recommendation_project.wsgi:application"]
