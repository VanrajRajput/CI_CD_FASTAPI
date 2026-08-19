# FastAPI CI/CD (ECR + EC2)

Production-style FastAPI service: pinned deps, non-root Docker image, health checks, pytest gate, then GitHub Actions → Amazon ECR → EC2.

Same path you use for an ML inference API later: keep training offline, serve `predict` from FastAPI, only ship a tested image.

```text
pytest  →  docker build  →  push Amazon ECR  →  pull & run on EC2
```

PRs: tests + image build. Push to `main`: also push to ECR and restart the container.

## Stack

| Piece | Role |
|---|---|
| FastAPI + Uvicorn (2 workers) | HTTP API |
| pytest | CI gate |
| Docker (non-root, healthcheck) | Runtime image |
| GitHub Actions | CI/CD |
| Amazon ECR | Registry |
| EC2 + self-hosted runner | Host |

**Env vars:** `APP_NAME`, `APP_ENV`, `APP_VERSION`, `LOG_LEVEL`  
Copy `.env.example` → `.env` (`.env` is gitignored).

Swagger (`/docs`) is on when `APP_ENV` is not `production`.

## Layout

```text
main.py
test_main.py
requirements.txt          # pinned
.env.example
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

## Local

```bash
cp .env.example .env
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
uvicorn main:app --reload --port 8000
```

- http://localhost:8000
- http://localhost:8000/health
- http://localhost:8000/docs  (non-production)

```bash
docker compose up --build
```

## CI/CD

`.github/workflows/ci.yml`

| Job | When | What |
|---|---|---|
| `test` | PR + `main` | install + `pytest -q` |
| `docker` | after tests | build; on `main` push `latest` + commit SHA to ECR |
| `deploy` | `main` only | EC2 runner pulls image, replaces `fastapi-app`, **80 → 8000** |

Live URL: `http://<EC2-public-IP>/` and `/health`.

### GitHub secrets

Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret |
| `AWS_DEFAULT_REGION` | e.g. `ap-south-1` |
| `ECR_REPO` | ECR **repository name** |

IAM: `ecr:GetAuthorizationToken` plus push/pull on that repo. Create the ECR repo before the first `main` deploy.

### EC2

1. Docker installed  
2. [Self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners) (`runs-on: self-hosted`)  
3. Security group: **80** (HTTP), **22** (SSH)  
4. Network path to ECR  

Deploy stops/removes the old `fastapi-app` container. AWS keys are not injected into the app. Rollback: pull a SHA tag from ECR and run that image.

## Production notes

- Image runs as uid `1000`, not root  
- `/health` is what Docker/ALB should probe  
- Pin versions in `requirements.txt`; bump deliberately  
- Do not commit `.env` or AWS keys  
- Put a TLS load balancer in front of port 80 before real public traffic  

License: MIT.
