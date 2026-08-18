import os

from fastapi import FastAPI

APP_NAME = os.getenv("APP_NAME", "ci-cd-demo")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(title=APP_NAME, version=APP_VERSION)


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
