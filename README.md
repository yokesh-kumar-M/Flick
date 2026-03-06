# Flick 🎬

Flick is a microservices-based streaming platform backend built with Django, Django REST Framework, Redis, and Celery.

## Architecture

The system is composed of the following services:
- **Gateway**: Serves the frontend Django templates and proxies requests.
- **Auth Service**: User authentication and profile management using JWTs.
- **Catalog Service**: Manages movies, tv shows, and their metadata.
- **Access Service**: Handles user access control and payment/subscription verification.
- **Streaming Service**: Streams video content to users securely.
- **Recommendation Service**: Analyzes watch history and provides movie recommendations.
- **Notification Service**: Sends notifications and alerts to users.

Each microservice is built using Django and follows a robust monolithic-styled distributed architecture.

## Deployment

### Render (Recommended for microservices)
Flick includes a `render.yaml` Blueprint which automatically provisions the 7 web services and 1 Redis instance.
Connect this repository to Render and click "New Blueprint" to deploy the entire stack automatically.

### Vercel
Alternatively, if you wish to run the Gateway on Vercel as serverless functions, you can configure Vercel to run the `gateway` WSGI application via `vercel.json` (serverless python execution).

## Local Development

To run locally, simply use the provided batch script:
```bash
./run_all.bat
```
*(Requires Python, Pip, and optionally Redis for caching/Celery jobs).*
