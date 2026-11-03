from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import AppError


def error_body(code: str, message: str, fields: list | None = None) -> dict:
    body = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return body


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        fields = []
        for err in exc.errors():
            loc = err["loc"]
            name = ".".join(str(part) for part in loc[1:]) or str(loc[0])
            fields.append({"field": name, "problem": err["msg"]})
        return JSONResponse(
            status_code=422,
            content=error_body("validation_error", "Some inputs are invalid", fields),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body("http_error", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=error_body("server_error", "Something went wrong on our side"),
        )