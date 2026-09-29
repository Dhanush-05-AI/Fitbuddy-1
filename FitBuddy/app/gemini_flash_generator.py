import os

from .gemini_client import generate_text


def generate_nutrition_tip_with_flash(goal):
    model = os.getenv("GEMINI_TIP_MODEL", "gemini-2.5-flash")
    prompt = f"""
Give one concise, practical nutrition or recovery tip for a general fitness app.
The user's goal is: {goal}

Keep it balanced and health-focused. Do not give restrictive calorie targets,
starvation advice, dehydration advice, or supplement prescriptions.
Mention ordinary food, hydration, sleep, or recovery habits where appropriate.
Return 2-4 sentences of plain text.
"""
    return generate_text(model, prompt, temperature=0.5)
