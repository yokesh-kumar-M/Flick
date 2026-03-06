FROM python:3.11-slim
WORKDIR /app
COPY access_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/access_service
RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN python manage.py migrate
EXPOSE 8003
CMD ["gunicorn", "--bind", "0.0.0.0:8003", "access_project.wsgi:application"]
