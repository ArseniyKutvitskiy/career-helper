import json
import os
import re
from google import genai
from google.genai import types

# Актуальная стабильная Flash-модель с бесплатным уровнем Gemini Developer API.
MODEL = "gemini-3.5-flash"

QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "category": {"type": "string"},
        "hint": {"type": "string"},
    },
    "required": ["question", "category", "hint"],
}

FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 1, "maximum": 10},
        "summary": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "improvements": {"type": "array", "items": {"type": "string"}},
        "improved_answer": {"type": "string"},
        "next_tip": {"type": "string"},
    },
    "required": ["score", "summary", "strengths", "improvements", "improved_answer", "next_tip"],
}

def _client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не задан на сервере.")
    return genai.Client(api_key=api_key)

def _json_response(prompt, schema):
    # Держим клиент открытым до получения ответа. Иначе временный объект может
    # быть уничтожен Python раньше, чем SDK завершит HTTP-запрос.
    with _client() as client:
        response = client.models.generate_content(
            model=MODEL, contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.2,
            ),
        )
    raw = re.sub(r"^\`\`\`(?:json)?\s*|\s*\`\`\`$", "", response.text.strip())
    return json.loads(raw)

def generate_question(role, vacancy_description="", mode="technical"):
    modes = {
        "technical": "техническое интервью: проверь практические знания и принятие решений",
        "hr": "HR/поведенческое интервью: проверь мотивацию, коммуникацию и примеры опыта",
        "system": "системный дизайн: проверь архитектурное мышление, масштабирование и компромиссы",
        "english": "собеседование на английском: задай вопрос на английском и оценивай ответ на английском",
        "express": "экспресс-интервью: задай короткий, но содержательный вопрос на один важный навык",
    }
    prompt = f'''Ты — опытный интервьюер. Сгенерируй ОДИН реалистичный вопрос для кандидата.
Роль: {role}
Режим: {modes.get(mode, modes["technical"])}
Описание вакансии (может быть пустым): {vacancy_description}
Верни только JSON: {{"question":"...", "category":"Технический или Поведенческий", "hint":"краткая подсказка"}}.
Пиши на русском, кроме режима английского. Вопрос должен проверять важный для роли навык.'''
    data = _json_response(prompt, QUESTION_SCHEMA)
    return {"question": str(data.get("question", "")), "category": str(data.get("category", "")), "hint": str(data.get("hint", ""))}

def evaluate_answer(role, question, answer, mode="technical"):
    prompt = f'''Ты — доброжелательный, но требовательный интервьюер. Оцени ответ кандидата.
Роль: {role}
Режим: {mode}
Вопрос: {question}
Ответ кандидата: {answer}
Верни только JSON: {{"score": число 1-10, "summary":"краткий вердикт", "strengths":["сильная сторона"], "improvements":["конкретное улучшение"], "improved_answer":"пример сильного ответа", "next_tip":"один совет"}}.
Пиши на русском. Будь конкретным, учитывай точность, структуру и полноту.'''
    data = _json_response(prompt, FEEDBACK_SCHEMA)
    try:
        score = max(1, min(10, int(data.get("score", 0))))
    except (TypeError, ValueError):
        score = 0
    return {"score": score, "summary": str(data.get("summary", "")), "strengths": data.get("strengths", []), "improvements": data.get("improvements", []), "improved_answer": str(data.get("improved_answer", "")), "next_tip": str(data.get("next_tip", ""))}
