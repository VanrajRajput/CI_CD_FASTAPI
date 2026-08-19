import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "ci-cd-demo")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("app")

docs_enabled = APP_ENV != "production"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
)


@app.get("/")
def read_root():
    return {
        "message": f"Hello from {APP_NAME}",
        "env": APP_ENV,
        "version": APP_VERSION,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {
        "app_name": APP_NAME,
        "app_env": APP_ENV,
        "app_version": APP_VERSION,
    }


logger.info("started %s env=%s version=%s", APP_NAME, APP_ENV, APP_VERSION)
