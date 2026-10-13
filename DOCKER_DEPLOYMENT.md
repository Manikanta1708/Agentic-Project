# Docker Deployment Guide

This guide provides instructions for containerizing, testing, and deploying the **Adaptive Graph-Augmented Hybrid Retrieval (AGHR) Curriculum Intelligence Dashboard** with Docker.

---

## 📋 Features of the Docker Setup

- **Lightweight & Fast:** Uses `python:3.11-slim` with multi-layer pip caching.
- **Security Hardened:** Runs as a non-privileged system user (`appuser`).
- **Dynamic Port Binding:** Supports standard port `8501` as well as cloud-provided dynamic `$PORT` environments (e.g. AWS App Runner, Google Cloud Run, Render, Heroku).
- **Automated Healthcheck:** Integrated Streamlit healthcheck endpoint (`/_stcore/health`) to enable auto-healing in orchestrators (Docker Compose, Kubernetes, AWS ECS).
- **Environment Isolation:** Zero host machine pollution; dependencies (`faiss-cpu`, `sentence-transformers`, `pyvis`, `networkx`, `streamlit`) are encapsulated.

---

## 🚀 Quick Start with Docker Compose (Recommended)

### 1. Build and Run Container

From the project root (or workspace root), run:

```bash
docker compose up --build -d
```

### 2. Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

### 3. Check Status and Logs

```bash
# Check container status & healthcheck
docker compose ps

# Follow application logs
docker compose logs -f dashboard
```

### 4. Stop Container

```bash
docker compose down
```

---

## 🛠️ Running with Docker CLI

If you prefer building and running directly with the `docker` CLI:

### 1. Build the Docker Image

```bash
docker build -t agentic-curriculum-dashboard:latest .
```

### 2. Run the Container

```bash
docker run -d \
  --name agentic-curriculum-dashboard \
  -p 8501:8501 \
  --restart unless-stopped \
  agentic-curriculum-dashboard:latest
```

### 3. Verify Health Status

```bash
docker inspect --format='{{json .State.Health.Status}}' agentic-curriculum-dashboard
```

---

## ⚙️ Configuration & Environment Variables

You can configure runtime settings via `.env` file or environment variables:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8501` | Port exposed by container |
| `STREAMLIT_SERVER_PORT` | `8501` | Streamlit internal server port |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Bind address |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Runs Streamlit without browser popups |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | `false` | Disables telemetry reporting |

To run on a custom port (e.g., `8080`):
```bash
PORT=8080 docker compose up -d
```
or with Docker CLI:
```bash
docker run -d -p 8080:8080 -e PORT=8080 agentic-curriculum-dashboard:latest
```

---

## ☁️ Cloud Deployment Recipes

### 1. Google Cloud Run
```bash
# Build and submit image to Google Artifact Registry
gcloud builds submit --tag gcr.io/<PROJECT-ID>/agentic-dashboard:latest

# Deploy with automatic HTTPS & dynamic PORT handling
gcloud run deploy agentic-dashboard \
  --image gcr.io/<PROJECT-ID>/agentic-dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi
```

### 2. AWS App Runner or ECS Fargate
1. Authenticate Docker with Amazon ECR:
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
   ```
2. Tag and push image:
   ```bash
   docker tag agentic-curriculum-dashboard:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/agentic-dashboard:latest
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/agentic-dashboard:latest
   ```
3. Create App Runner service with port `8501`.

### 3. Render / DigitalOcean App Platform
1. Connect your Git repository.
2. Select **Docker** as environment runtime.
3. Render/DigitalOcean will detect `Dockerfile` and expose the service automatically.
