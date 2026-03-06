FROM python:3.11-slim

WORKDIR /app

COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/auth_service

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "auth_project.wsgi:application"]
