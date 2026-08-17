"""Unit tests for learning application Class-Based Views."""

from unittest.mock import MagicMock, patch
import pytest
from django.urls import reverse

from learning.models import Essay, Feedback, Topic
from services.llm_analyzer import LLMAnalysisError


@pytest.mark.django_db
def test_topic_list_view(client) -> None:
    """Test TopicListView renders successfully with topic instances."""
    topic1 = Topic.objects.create(title="Edukacja w Polsce", description="Opisz system edukacji.")
    topic2 = Topic.objects.create(title="Ekologia", description="Ochrona środowiska.")

    url = reverse("learning:topic-list")
    response = client.get(url)

    assert response.status_code == 200
    assert "learning/topic_list.html" in [t.name for t in response.templates]
    assert len(response.context["topics"]) == 2
    assert topic1 in response.context["topics"]
    assert topic2 in response.context["topics"]


@pytest.mark.django_db
def test_essay_create_view_get(client) -> None:
    """Test EssayCreateView GET request renders form with topic context."""
    topic = Topic.objects.create(title="Kultura i sztuka", description="Zacznij pisać.")
    url = reverse("learning:essay-create", kwargs={"topic_id": topic.id})

    response = client.get(url)

    assert response.status_code == 200
    assert "learning/essay_form.html" in [t.name for t in response.templates]
    assert response.context["topic"] == topic


@pytest.mark.django_db
def test_essay_create_view_post_success(client) -> None:
    """Test valid essay submission triggers LLMAnalyzer and creates Feedback record."""
    topic = Topic.objects.create(title="Podróże", description="Opisz podróż.")
    url = reverse("learning:essay-create", kwargs={"topic_id": topic.id})

    mock_results = {
        "corrected_text": "Podróżowanie kształci.",
        "errors": ["Poprawiono interpunkcję."],
        "advanced_synonyms": [
            {"original": "lubię", "suggestion": "uwielbiam", "explanation": "Poziom C1"}
        ]
    }

    with patch("learning.views.LLMAnalyzer") as mock_analyzer_cls:
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_essay.return_value = mock_results
        mock_analyzer_cls.return_value = mock_analyzer_instance

        post_data = {"content": "Podrozowanie ksztalci."}
        response = client.post(url, post_data)

        # Check essay created
        assert Essay.objects.count() == 1
        essay = Essay.objects.first()
        assert essay.content == "Podrozowanie ksztalci."
        assert essay.topic == topic

        # Check feedback created
        assert Feedback.objects.count() == 1
        feedback = Feedback.objects.first()
        assert feedback.essay == essay
        assert feedback.corrected_text == "Podróżowanie kształci."

        # Check redirect to feedback detail
        expected_url = reverse("learning:feedback-detail", kwargs={"pk": feedback.pk})
        assert response.status_code == 302
        assert response.url == expected_url


@pytest.mark.django_db
def test_essay_create_view_post_llm_error_fallback(client) -> None:
    """Test essay submission handles LLMAnalysisError gracefully with fallback."""
    topic = Topic.objects.create(title="Technologia")
    url = reverse("learning:essay-create", kwargs={"topic_id": topic.id})

    with patch("learning.views.LLMAnalyzer") as mock_analyzer_cls:
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_essay.side_effect = LLMAnalysisError("API Key Invalid")
        mock_analyzer_cls.return_value = mock_analyzer_instance

        response = client.post(url, {"content": "Nowe technologie w życiu."})

        assert Essay.objects.count() == 1
        assert Feedback.objects.count() == 1
        feedback = Feedback.objects.first()
        assert feedback.corrected_text == "Nowe technologie w życiu."
        assert response.status_code == 302


@pytest.mark.django_db
def test_feedback_detail_view(client) -> None:
    """Test FeedbackDetailView renders feedback information."""
    topic = Topic.objects.create(title="Sztuczna Inteligencja")
    essay = Essay.objects.create(topic=topic, content="AI zmienia świat.")
    feedback = Feedback.objects.create(
        essay=essay,
        corrected_text="Sztuczna inteligencja zmienia świat.",
        feedback_json={"errors": [], "advanced_synonyms": []}
    )

    url = reverse("learning:feedback-detail", kwargs={"pk": feedback.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert "learning/feedback_detail.html" in [t.name for t in response.templates]
    assert response.context["feedback"] == feedback
