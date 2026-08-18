import json
import os
import re
import time
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
        "plain_explanation": {"type": "string"},
        "term_explanations": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
        "knowledge_score": {"type": "integer", "minimum": 1, "maximum": 10},
        "structure_score": {"type": "integer", "minimum": 1, "maximum": 10},
        "clarity_score": {"type": "integer", "minimum": 1, "maximum": 10},
    },
    "required": ["score", "summary", "strengths", "improvements", "improved_answer", "next_tip", "plain_explanation", "term_explanations", "next_step", "knowledge_score", "structure_score", "clarity_score"],
}

def _client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не задан на сервере.")
    return genai.Client(api_key=api_key)

def _json_response(prompt, schema):
    # Повторяем один раз: это сглаживает краткие сбои сети, перегрузку или
    # единичный неудачный JSON-ответ, не превращая запрос в бесконечный цикл.
    last_error = None
    for attempt in range(2):
        try:
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
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Gemini вернул ответ не в формате объекта.")
            return data
        except Exception as error:
            last_error = error
            if attempt == 0:
                time.sleep(1)
    raise last_error

def generate_question(role, vacancy_description="", mode="technical"):
    modes = {
        "technical": "техническое интервью: проверь практические знания и принятие решений",
        "hr": "HR/поведенческое интервью: проверь мотивацию, коммуникацию и примеры опыта",
        "system": "системный дизайн: проверь архитектурное мышление, масштабирование и компромиссы",
        "english": "собеседование на английском: задай вопрос на английском и оценивай ответ на английском",
        "express": "экспресс-интервью: задай короткий, но содержательный вопрос на один важный навык",
    }
    prompt = f'''Ты — спокойный наставник, который готовит Junior/Middle-кандидата к собеседованию. Сгенерируй ОДИН реалистичный вопрос.
Роль: {role}
Режим: {modes.get(mode, modes["technical"])}
Описание вакансии (может быть пустым): {vacancy_description}
Верни только JSON: {{"question":"...", "category":"Технический или Поведенческий", "hint":"краткая подсказка простыми словами"}}.
Пиши на русском, кроме режима английского. Избегай редких терминов; если без термина нельзя, поясни его в скобках. Вопрос должен быть конкретным и посильным для уровня Junior/Middle.'''
    data = _json_response(prompt, QUESTION_SCHEMA)
    return {"question": str(data.get("question", "")), "category": str(data.get("category", "")), "hint": str(data.get("hint", ""))}

def evaluate_answer(role, question, answer, mode="technical"):
    prompt = f'''Ты — терпеливый наставник для Junior/Middle-кандидата, а не строгий экзаменатор. Оцени ответ на интервью.
Роль: {role}
Режим: {mode}
Вопрос: {question}
Ответ кандидата: {answer}
Верни только JSON с полями: score (1-10), summary, strengths, improvements, improved_answer, next_tip, plain_explanation, term_explanations, next_step, knowledge_score (1-10), structure_score (1-10), clarity_score (1-10).
Правила:
- Пиши простым, доброжелательным русским языком. Не используй сложный термин без расшифровки.
- plain_explanation: объясни главную тему вопроса как начинающему в 2-3 коротких предложениях.
- term_explanations: до 3 строк вида "Термин — простое объяснение". Если терминов нет, верни пустой список.
- improved_answer: максимум 6 коротких предложений; он должен звучать естественно на собеседовании, а не как учебник.
- improvements: максимум 3 конкретных шага.
- Если кандидат написал, что не знает или ответ очень слабый: не стыди его. Кратко объясни тему с нуля, дай безопасный шаблон ответа и один маленький следующий шаг.
- Оценивай знания, структуру и ясность отдельно. Пиши на русском, кроме режима english.'''
    data = _json_response(prompt, FEEDBACK_SCHEMA)
    try:
        score = max(1, min(10, int(data.get("score", 0))))
    except (TypeError, ValueError):
        score = 0
    def text_list(value):
        return [str(item) for item in value] if isinstance(value, list) else []

    def safe_score(name):
        try:
            return max(1, min(10, int(data.get(name, score))))
        except (TypeError, ValueError):
            return score

    return {
        "score": score, "summary": str(data.get("summary", "")),
        "strengths": text_list(data.get("strengths")), "improvements": text_list(data.get("improvements")),
        "improved_answer": str(data.get("improved_answer", "")), "next_tip": str(data.get("next_tip", "")),
        "plain_explanation": str(data.get("plain_explanation", "")),
        "term_explanations": text_list(data.get("term_explanations")), "next_step": str(data.get("next_step", "")),
        "knowledge_score": safe_score("knowledge_score"), "structure_score": safe_score("structure_score"),
        "clarity_score": safe_score("clarity_score"),
    }
