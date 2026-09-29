import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .gemini_client import GeminiError
from .routes import router, templates

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("fitbuddy")
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description="AI-powered 7-day fitness plan generator using FastAPI and Gemini.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)


def _error_page(request: Request, status: int, title: str, message: str, headers=None):
    return templates.TemplateResponse(
        request, "error.html", {"title": title, "message": message}, status_code=status, headers=headers
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = first["loc"][-1] if first["loc"] else "input"
    return _error_page(request, 422, "Check your details", f"{field}: {first['msg']}")


@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException):
    return _error_page(request, exc.status_code, f"Error {exc.status_code}", str(exc.detail), exc.headers)


@app.exception_handler(GeminiError)
async def gemini_handler(request: Request, exc: GeminiError):
    logger.error("Gemini failure: %s", exc)
    return _error_page(
        request, 502, "AI service unavailable",
        "FitBuddy couldn't reach the AI service. Check your API key or try again in a moment.",
    )
