"""
Domain exceptions raised by the service layer.

Services stay HTTP-agnostic: they raise these, and `register_exception_handlers`
maps them (and database failures) to HTTP responses in one place.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

logger = logging.getLogger("employee_api")


class AppError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidSearchQueryError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST


class EmployeeNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class DuplicateEmployeeError(AppError):
    status_code = status.HTTP_409_CONFLICT


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = [
            f"{' -> '.join(str(loc) for loc in err.get('loc', []))}: {err.get('msg', 'Invalid value')}"
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"detail": "Request validation failed", "errors": errors},
        )

    @app.exception_handler(OperationalError)
    async def db_unavailable_handler(request: Request, exc: OperationalError):
        logger.error("Database unavailable: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database service is currently unavailable. Please try again later."},
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occurred while processing the request."},
        )
