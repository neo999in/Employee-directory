"""Every error becomes a JSON {"detail": "..."} response here, in one place."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

logger = logging.getLogger("employee_api")


class InvalidSearchQueryError(Exception):
    """Raised by the service for a bad search value (-> 400)."""


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidSearchQueryError)
    async def invalid_search(request: Request, exc: InvalidSearchQueryError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def invalid_params(request: Request, exc: RequestValidationError):
        errors = [f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": "Invalid query parameters", "errors": errors})

    @app.exception_handler(OperationalError)
    async def db_unavailable(request: Request, exc: OperationalError):
        logger.error("Database unavailable: %s", exc)
        return JSONResponse(status_code=503, content={"detail": "Database is unavailable. Please try again later."})

    @app.exception_handler(SQLAlchemyError)
    async def db_error(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error")
        return JSONResponse(status_code=500, content={"detail": "Unexpected database error."})
