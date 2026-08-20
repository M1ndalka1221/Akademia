"""Unit tests for Daily AI Quizzes and Interactive Essay Correction Mode."""

import json
from unittest.mock import MagicMock, patch
import pytest
from django.test import override_settings
from django.urls import reverse

from learning.models import Essay, Feedback, Topic, Vocabulary
from services.llm_analyzer import LLMAnalysisError, LLMAnalyzer


@pytest.mark.django_db
def test_quiz_view_get(client) -> None:
    """Test QuizView GET renders quiz page with generated quiz questions."""
    Vocabulary.objects.create(word="zawiłość", translation="сложность")
    Vocabulary.objects.create(word="skrupulatność", translation="скрупулезность")

    url = reverse("learning:quiz-detail")
    response = client.get(url)

    assert response.status_code == 200
    assert "learning/quiz_detail.html" in [t.name for t in response.templates]
    assert "questions" in response.context
    assert "quiz_json" in response.context
    assert response.context["total_questions"] == 5


@override_settings(DEBUG=True)
def test_llm_analyzer_generate_vocabulary_quiz_demo_fallback() -> None:
    """Test LLMAnalyzer quiz generation fallback in DEBUG mode."""
    analyzer = LLMAnalyzer(api_key="")
    questions = analyzer.generate_vocabulary_quiz(count=5)

    assert isinstance(questions, list)
    assert len(questions) == 5
    assert "question" in questions[0]
    assert "options" in questions[0]
    assert len(questions[0]["options"]) == 4


@pytest.mark.django_db
def test_essay_correction_validate_view_post(client) -> None:
    """Test EssayCorrectionValidateView AJAX endpoint returns validation JSON."""
    topic = Topic.objects.create(title="Test Topic")
    essay = Essay.objects.create(topic=topic, content="Test treść eseju z błędem.")
    feedback = Feedback.objects.create(
        essay=essay,
        corrected_text="Test treść eseju bez błędu.",
        feedback_json={"errors": ["Użyto złego spójnika."]}
    )

    url = reverse("learning:essay-correct-validate", kwargs={"pk": feedback.pk})
    post_data = {
        "original_error": "Użyto złego spójnika.",
        "user_rewrite": "Zamiast tego użyłem spójnika ponadtowtórnie w pełnym zdaniu C1."
    }

    response = client.post(
        url,
        data=json.dumps(post_data),
        content_type="application/json"
    )

    assert response.status_code == 200
    res_data = json.loads(response.content.decode("utf-8"))
    assert res_data["success"] is True
    assert "result" in res_data
    assert "is_correct" in res_data["result"]
    assert "feedback" in res_data["result"]


@override_settings(DEBUG=True)
def test_llm_analyzer_validate_sentence_correction_demo_fallback() -> None:
    """Test LLMAnalyzer sentence correction validation demo fallback."""
    analyzer = LLMAnalyzer(api_key="")
    res = analyzer.validate_sentence_correction(
        original_error="Brak precyzji słownej",
        user_rewrite="Zważywszy na obecną sytuację, należy podjąć stanowcze kroki."
    )

    assert res["is_correct"] is True
    assert "feedback" in res
    assert "improved_suggestion" in res
