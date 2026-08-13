from fastapi import FastAPI

app = FastAPI(
    title="Hakimi API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Hakimi backend is ready"
    }


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "backend"
    }
