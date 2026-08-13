from fastapi import APIRouter

from app.db.session import test_database_connection


router = APIRouter()


@router.get("/health")
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
