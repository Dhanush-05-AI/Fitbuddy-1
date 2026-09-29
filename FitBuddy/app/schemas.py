from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

USER_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=1, max_length=100, pattern=USER_ID_PATTERN)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: Literal[
        "general wellness", "muscle gain", "weight loss", "flexibility", "cardio fitness"
    ]
    intensity: Literal["low", "medium", "high"]


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=1, max_length=100, pattern=USER_ID_PATTERN)
    feedback: str = Field(min_length=1, max_length=2000)
