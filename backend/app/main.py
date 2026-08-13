from fastapi import FastAPI

from app.db.session import test_database_connection

app = FastAPI(
    title="Hakimi API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Hakimi API is running"
    }


@app.get("/api/v1/health")
def health_check():
    try:
        db_result = test_database_connection()

        return {
            "status": "ok",
            "backend": "ok",
            "database": "ok",
            "database_test": db_result,
        }

    except Exception as exc:
        return {
            "status": "error",
            "backend": "ok",
            "database": "error",
            "detail": str(exc),
        }
