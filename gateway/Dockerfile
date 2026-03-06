FROM python:3.11-slim
WORKDIR /app
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/gateway
RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN python manage.py migrate
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gateway_project.wsgi:application"]
