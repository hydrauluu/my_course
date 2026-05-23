from app.config import settings

REVIEW_SYSTEM_PROMPT = """Ты — AI-ассистент преподавателя курса Python Engineering Course.
Твоя задача — анализировать домашние задания студентов.

Для заданий типа A (код):
1. Проверь, запускается ли код без ошибок
2. Проверь тесты, если есть
3. Проанализируй стиль и идиоматичность Python
4. Задай уточняющий вопрос

Для заданий типа B (объяснение):
1. Прочитай PR description как объяснение студента
2. Оцени по шкале 0-3:
   0 — Синтаксис: перечисление конструкций
   1 — Операции: пошаговое описание
   2 — Цель: назначение функции/кода
   3 — Контекст: роль в системе
3. Дай конкретную обратную связь
4. Задай уточняющий вопрос

Для заданий типа AB (код + объяснение):
1. Проверь код (как в типе A)
2. Проверь тесты, если есть
3. Проанализируй стиль
4. Прочитай PR description как объяснение студента
5. Оцени понимание по шкале 0-3 (как в типе B)
6. Задай уточняющий вопрос

Формат ответа для типа A:
✅ Код запускается без ошибок
✅ Тесты пройдены (X/Y)
📝 Стиль: ...
💡 Концепция лекции: ...
❓ Вопрос: ...

Формат ответа для типа B:
📄 Объяснение прочитано из PR description
📊 Уровень понимания (предварительно): X — Название
   ...
❓ Вопрос: ...

Формат ответа для типа AB:
## Код
✅ Код запускается без ошибок
✅ Тесты пройдены (X/Y)
📝 Стиль: ...
💡 Концепция лекции: ...

## Объяснение
📄 Объяснение прочитано из PR description
📊 Уровень понимания (предварительно): X — Название

❓ Вопрос: ..."""


async def run_ai_review(assignment_type: str, code_diff: str | None, pr_description: str | None, lecture_context: str) -> str:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured — cannot run AI review")

    try:
        from google import genai

        client = genai.aio.Client(api_key=settings.GEMINI_API_KEY)

        user_content = f"Контекст лекции: {lecture_context}\n\n"
        if assignment_type == "A" and code_diff:
            user_content += f"Код из PR (diff):\n{code_diff}\n\n"
        elif assignment_type == "B" and pr_description:
            user_content += f"PR description (объяснение студента):\n{pr_description}\n\n"
        elif assignment_type == "AB":
            if code_diff:
                user_content += f"Код из PR (diff):\n{code_diff}\n\n"
            if pr_description:
                user_content += f"PR description (объяснение студента):\n{pr_description}\n\n"

        response = await client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_content,
            config=genai.types.GenerateContentConfig(
                system_instruction=REVIEW_SYSTEM_PROMPT,
                max_output_tokens=2000,
            ),
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def parse_review_response(response: str, assignment_type: str) -> dict:
    result = {
        "runs_without_errors": None,
        "tests_passed": None,
        "style_comments": None,
        "logic_comments": None,
        "clarifying_question": None,
        "predicted_level": None,
        "raw_response": response,
    }

    if assignment_type == "A":
        if "✅ Код запускается без ошибок" in response:
            result["runs_without_errors"] = True
        if "✅ Тесты пройдены" in response:
            import re
            match = re.search(r"✅ Тесты пройдены \((\d+)/(\d+)\)", response)
            if match:
                result["tests_passed"] = f"{match.group(1)}/{match.group(2)}"

        for prefix in ["📝 Стиль:", "💡 Концепция лекции:"]:
            for line in response.split("\n"):
                if line.startswith(prefix):
                    result["style_comments"] = line.replace(prefix, "").strip()

        for line in response.split("\n"):
            if line.startswith("❓ Вопрос:"):
                result["clarifying_question"] = line.replace("❓ Вопрос:", "").strip()
    elif assignment_type == "AB":
        if "✅ Код запускается без ошибок" in response:
            result["runs_without_errors"] = True
        if "✅ Тесты пройдены" in response:
            import re
            match = re.search(r"✅ Тесты пройдены \((\d+)/(\d+)\)", response)
            if match:
                result["tests_passed"] = f"{match.group(1)}/{match.group(2)}"

        for prefix in ["📝 Стиль:", "💡 Концепция лекции:"]:
            for line in response.split("\n"):
                if line.startswith(prefix):
                    result["style_comments"] = line.replace(prefix, "").strip()

        import re
        match = re.search(r"Уровень понимания \(предварительно\):\s*(\d+)", response)
        if match:
            result["predicted_level"] = float(match.group(1))

        for line in response.split("\n"):
            if line.startswith("❓ Вопрос:"):
                result["clarifying_question"] = line.replace("❓ Вопрос:", "").strip()

        result["logic_comments"] = response
    else:
        import re
        match = re.search(r"Уровень понимания \(предварительно\):\s*(\d+)", response)
        if match:
            result["predicted_level"] = float(match.group(1))

        for line in response.split("\n"):
            if line.startswith("❓ Вопрос:"):
                result["clarifying_question"] = line.replace("❓ Вопрос:", "").strip()

        result["logic_comments"] = response

    return result


def mock_review(assignment_type: str, pr_description: str | None) -> str:
    if assignment_type == "A":
        return (
            "✅ Код запускается без ошибок\n"
            "✅ Тесты пройдены (3/3)\n"
            "📝 Стиль: хороший идиоматичный код, но можно использовать list comprehension\n"
            "💡 Концепция лекции: правильно применён протокол итерации\n"
            "❓ Вопрос: Почему ты выбрал именно этот подход?"
        )
    elif assignment_type == "AB":
        return (
            "## Код\n"
            "✅ Код запускается без ошибок\n"
            "✅ Тесты пройдены (3/3)\n"
            "📝 Стиль: хороший идиоматичный код, но можно использовать list comprehension\n"
            "💡 Концепция лекции: правильно применён протокол итерации\n"
            "\n"
            "## Объяснение\n"
            "📄 Объяснение прочитано из PR description\n"
            "📊 Уровень понимания (предварительно): 2 — Цель\n"
            "   Ты описываешь что делает функция — это хорошо.\n"
            "   Чтобы выйти на уровень 3, объясни в каком контексте системы она вызывается.\n"
            "\n"
            "❓ Вопрос: Почему Django использует здесь __new__ вместо __init__?"
        )
    else:
        return (
            "📄 Объяснение прочитано из PR description\n"
            "📊 Уровень понимания (предварительно): 2 — Цель\n"
            "   Ты описываешь что делает функция — это хорошо.\n"
            "   Чтобы выйти на уровень 3, объясни в каком контексте системы она вызывается.\n"
            "❓ Вопрос: Почему Django использует здесь __new__ вместо __init__?"
        )
