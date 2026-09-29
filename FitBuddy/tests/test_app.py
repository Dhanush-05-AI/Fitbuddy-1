import base64
import importlib
import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["ADMIN_PASSWORD"] = "secret"

import pytest
from fastapi.testclient import TestClient

import run

from app import routes
from app.gemini_client import GeminiError
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Basic " + base64.b64encode(b"admin:secret").decode()}
FORM = dict(username="Asha", user_id="FB001", age="25", weight="60.5",
            goal="muscle gain", intensity="medium")


@pytest.fixture(autouse=True)
def fake_gemini(monkeypatch):
    monkeypatch.setattr(routes, "generate_workout_gemini", lambda *a: "Day 1 - Push")
    monkeypatch.setattr(routes, "generate_nutrition_tip_with_flash", lambda g: "Drink water.")
    monkeypatch.setattr(routes, "update_workout_plan", lambda cur, fb: cur + " | " + fb)


def test_pages_and_health():
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/static/style.css").status_code == 200


def test_generate_feedback_regenerate_flow():
    r = client.post("/generate-workout", data=FORM)
    assert r.status_code == 200 and "Day 1 - Push" in r.text
    r = client.post("/submit-feedback", data={"user_id": "FB001", "feedback": "more cardio"})
    assert "Day 1 - Push | more cardio" in r.text
    r = client.post("/submit-feedback", data={"user_id": "FB001", "feedback": "rest day"})
    assert "more cardio | rest day" in r.text
    r = client.post("/generate-workout", data={**FORM, "goal": "flexibility"})
    assert r.status_code == 200
    assert "flexibility" in client.get("/view-all-users", headers=AUTH).text


def test_validation_errors():
    assert client.post("/generate-workout", data={**FORM, "intensity": "extreme"}).status_code == 422
    assert client.post("/generate-workout", data={**FORM, "age": "5"}).status_code == 422
    assert client.post("/generate-workout", data={**FORM, "user_id": "a b/c"}).status_code == 422
    assert client.post("/submit-feedback", data={"user_id": "NOPE", "feedback": "x"}).status_code == 404


def test_admin_protection_and_delete():
    client.post("/generate-workout", data={**FORM, "user_id": "FB002"})
    assert client.get("/view-all-users").status_code == 401
    assert client.post("/delete-user/FB002", follow_redirects=False).status_code == 401
    r = client.post("/delete-user/FB002", headers=AUTH, follow_redirects=False)
    assert r.status_code == 303
    assert client.post("/delete-user/FB002", headers=AUTH).status_code == 404


def test_admin_disabled_without_password(monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD")
    assert client.get("/view-all-users", headers=AUTH).status_code == 503


def test_gemini_failure_shows_error_page(monkeypatch):
    def boom(*a):
        raise GeminiError("down")
    monkeypatch.setattr(routes, "generate_workout_gemini", boom)
    r = client.post("/generate-workout", data=FORM)
    assert r.status_code == 502 and "AI service unavailable" in r.text


def test_run_defaults_to_no_reload_on_windows(monkeypatch):
    calls = {}

    def fake_run(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs

    monkeypatch.setattr(run.uvicorn, "run", fake_run)
    monkeypatch.delenv("RELOAD", raising=False)
    monkeypatch.setattr(run.os, "name", "nt", raising=False)

    run.main()

    assert calls["kwargs"]["reload"] is False


def test_tip_failure_is_non_fatal(monkeypatch):
    def boom(g):
        raise GeminiError("down")
    monkeypatch.setattr(routes, "generate_nutrition_tip_with_flash", boom)
    r = client.post("/generate-workout", data={**FORM, "user_id": "FB003"})
    assert r.status_code == 200 and "not available" in r.text
