import logging
import os
import secrets
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from .database import delete_user, get_all_users, get_user, save_updated_plan, upsert_user
from .gemini_client import GeminiError
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini, update_workout_plan
from .schemas import FeedbackRequest, UserInput

logger = logging.getLogger("fitbuddy.routes")
BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
security = HTTPBasic()


def require_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> None:
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise HTTPException(503, "Admin dashboard is disabled. Set ADMIN_PASSWORD to enable it.")
    username = os.getenv("ADMIN_USERNAME", "admin")
    ok = secrets.compare_digest(credentials.username.encode(), username.encode())
    ok &= secrets.compare_digest(credentials.password.encode(), password.encode())
    if not ok:
        raise HTTPException(401, "Invalid admin credentials.", headers={"WWW-Authenticate": "Basic"})


def _render_result(request: Request, user, plan: str, message: str | None = None):
    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "username": user.username,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": plan,
            "nutrition_tip": user.nutrition_tip,
            "message": message,
        },
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(request: Request, data: Annotated[UserInput, Form()]):
    plan = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
    try:
        tip = generate_nutrition_tip_with_flash(data.goal)
    except GeminiError:
        logger.exception("Nutrition tip generation failed; saving plan without a tip")
        tip = None
    user = upsert_user(data.model_dump(), plan, tip)
    return _render_result(request, user, plan)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, data: Annotated[FeedbackRequest, Form()]):
    user = get_user(data.user_id)
    if not user or not user.original_plan:
        raise HTTPException(404, "User ID not found. Please generate a plan first.")
    # Build on the latest version so successive feedback accumulates.
    current = user.updated_plan or user.original_plan
    revised = update_workout_plan(current, data.feedback)
    save_updated_plan(user.user_id, revised)
    return _render_result(request, user, revised, "Your workout plan has been updated using your feedback.")


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    return templates.TemplateResponse(request, "all_users.html", {"users": get_all_users()})


@router.post("/delete-user/{user_id}")
def remove_user(user_id: str):
    if not delete_user(user_id):
        raise HTTPException(404, "User not found.")
    return RedirectResponse(url="/view-all-users", status_code=303)
