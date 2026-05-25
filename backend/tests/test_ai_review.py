import pytest
from app.services.ai_review import parse_review_response, mock_review


class TestParseReviewResponse:
    def test_type_a_full_response(self):
        response = (
            "✅ Код запускается без ошибок\n"
            "✅ Тесты пройдены (3/3)\n"
            "📝 Стиль: хороший идиоматичный код\n"
            "💡 Концепция лекции: верно применён протокол\n"
            "❓ Вопрос: Почему ты выбрал этот подход?"
        )
        result = parse_review_response(response, "A")
        assert result["runs_without_errors"] is True
        assert result["tests_passed"] == "3/3"
        assert result["style_comments"] == "верно применён протокол"
        assert result["clarifying_question"] == "Почему ты выбрал этот подход?"
        assert result["predicted_level"] is None

    def test_type_a_no_errors(self):
        response = "✅ Код запускается без ошибок\n❓ Вопрос: Как ты это сделал?"
        result = parse_review_response(response, "A")
        assert result["runs_without_errors"] is True
        assert result["tests_passed"] is None
        assert result["clarifying_question"] == "Как ты это сделал?"

    def test_type_a_empty_response(self):
        result = parse_review_response("", "A")
        assert result["runs_without_errors"] is None
        assert result["tests_passed"] is None
        assert result["style_comments"] is None
        assert result["clarifying_question"] is None
        assert result["predicted_level"] is None

    def test_type_a_partial_response(self):
        response = "✅ Тесты пройдены (5/5)\n"
        result = parse_review_response(response, "A")
        assert result["runs_without_errors"] is None
        assert result["tests_passed"] == "5/5"

    def test_type_b_full_response(self):
        response = (
            "📄 Объяснение прочитано из PR description\n"
            "📊 Уровень понимания (предварительно): 2 — Цель\n"
            "   Ты описываешь что делает функция — это хорошо.\n"
            "❓ Вопрос: Почему Django использует здесь __new__?"
        )
        result = parse_review_response(response, "B")
        assert result["predicted_level"] == 2.0
        assert "Ты описываешь что делает функция" in result["logic_comments"]
        assert result["clarifying_question"] == "Почему Django использует здесь __new__?"
        assert result["runs_without_errors"] is None

    def test_type_b_no_level(self):
        response = "📄 Объяснение прочитано из PR description\n❓ Вопрос: А что если?"
        result = parse_review_response(response, "B")
        assert result["predicted_level"] is None
        assert result["clarifying_question"] == "А что если?"

    def test_type_b_empty_response(self):
        result = parse_review_response("", "B")
        assert result["predicted_level"] is None
        assert result["logic_comments"] == ""

    def test_type_ab_full_response(self):
        response = (
            "## Код\n"
            "✅ Код запускается без ошибок\n"
            "✅ Тесты пройдены (3/3)\n"
            "📝 Стиль: хороший идиоматичный код\n"
            "\n"
            "## Объяснение\n"
            "📄 Объяснение прочитано из PR description\n"
            "📊 Уровень понимания (предварительно): 3 — Контекст\n"
            "\n"
            "❓ Вопрос: Какой контекст использования?"
        )
        result = parse_review_response(response, "AB")
        assert result["runs_without_errors"] is True
        assert result["tests_passed"] == "3/3"
        assert result["style_comments"] == "хороший идиоматичный код"
        assert result["predicted_level"] == 3.0
        assert result["clarifying_question"] == "Какой контекст использования?"
        assert result["logic_comments"] == response

    def test_type_ab_code_only(self):
        response = (
            "✅ Код запускается без ошибок\n"
            "📝 Стиль: отлично\n"
        )
        result = parse_review_response(response, "AB")
        assert result["runs_without_errors"] is True
        assert result["style_comments"] == "отлично"
        assert result["predicted_level"] is None

    def test_type_ab_empty_response(self):
        result = parse_review_response("", "AB")
        assert result["runs_without_errors"] is None
        assert result["style_comments"] is None
        assert result["predicted_level"] is None
        assert result["clarifying_question"] is None

    def test_unrecognized_type(self):
        response = "some random text"
        result = parse_review_response(response, "UNKNOWN")
        assert result["logic_comments"] == response

    def test_raw_response_always_present(self):
        response = "some text"
        result = parse_review_response(response, "A")
        assert result["raw_response"] == response

    def test_malformed_tests_match(self):
        response = "✅ Тесты пройдены (abc/def)"
        result = parse_review_response(response, "A")
        assert result["tests_passed"] is None


class TestMockReview:
    def test_mock_type_a(self):
        result = mock_review("A", None)
        assert "✅ Код запускается без ошибок" in result
        assert "❓ Вопрос:" in result

    def test_mock_type_b(self):
        result = mock_review("B", "test description")
        assert "📊 Уровень понимания" in result
        assert "❓ Вопрос:" in result

    def test_mock_type_ab(self):
        result = mock_review("AB", "test description")
        assert "## Код" in result
        assert "## Объяснение" in result
        assert "❓ Вопрос:" in result
