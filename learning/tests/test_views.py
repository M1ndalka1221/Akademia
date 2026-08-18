"""Unit tests for learning application views."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch
import pytest
from django.test import Client
from django.urls import reverse

from learning.models import Essay, Feedback, Topic


@pytest.mark.django_db
def test_topic_list_view(client: Client, sample_topic: Topic) -> None:
    """Test TopicListView returns 200 OK and lists topics."""
    url = reverse("learning:topic-list")
    response = client.get(url)

    assert response.status_code == 200
    assert sample_topic in response.context["topics"]


@pytest.mark.django_db
def test_essay_create_view_get(client: Client, sample_topic: Topic) -> None:
    """Test EssayCreateView GET renders essay_form.html with topic context."""
    url = reverse("learning:essay-create", kwargs={"topic_id": sample_topic.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["topic"] == sample_topic


@pytest.mark.django_db
def test_essay_create_view_post_with_mocked_llm(
    client: Client,
    sample_topic: Topic,
    mock_analysis_payload: Dict[str, Any]
) -> None:
    """
    Test EssayCreateView POST request.
    Mocks LLMAnalyzer.analyze_essay to verify view logic and feedback creation
    without making real external API calls.
    """
    url = reverse("learning:essay-create", kwargs={"topic_id": sample_topic.id})
    post_data = {"content": "Sztuczna inteligencja rozwija się bardzo szybko."}

    with patch("learning.views.LLMAnalyzer.analyze_essay") as mock_analyze:
        mock_analyze.return_value = mock_analysis_payload

        response = client.post(url, post_data)

        # 1. Verify LLMAnalyzer.analyze_essay was called once with essay content
        mock_analyze.assert_called_once_with("Sztuczna inteligencja rozwija się bardzo szybko.")

        # 2. Verify Essay instance was created and associated with sample_topic
        assert Essay.objects.count() == 1
        essay = Essay.objects.first()
        assert essay is not None
        assert essay.topic == sample_topic
        assert essay.content == "Sztuczna inteligencja rozwija się bardzo szybko."

        # 3. Verify Feedback instance was created with returned payload
        assert Feedback.objects.count() == 1
        feedback = Feedback.objects.first()
        assert feedback is not None
        assert feedback.essay == essay
        assert feedback.corrected_text == mock_analysis_payload["corrected_text"]
        assert feedback.feedback_json == mock_analysis_payload

        # 4. Verify HTTP redirect to FeedbackDetailView
        expected_url = reverse("learning:feedback-detail", kwargs={"pk": feedback.pk})
        assert response.status_code == 302
        assert response.url == expected_url


@pytest.mark.django_db
def test_user_topic_list_view(client: Client, sample_topic: Topic) -> None:
    """Test UserTopicListView lists only custom user-created topics."""
    custom_topic = Topic.objects.create(
        title="Mój własny temat",
        description="Opis własnego tematu",
        is_custom=True
    )
    url = reverse("learning:user-topic-list")
    response = client.get(url)

    assert response.status_code == 200
    assert custom_topic in response.context["topics"]
    assert sample_topic not in response.context["topics"]


@pytest.mark.django_db
def test_topic_create_view_get(client: Client) -> None:
    """Test TopicCreateView GET request renders topic_form.html."""
    url = reverse("learning:topic-create")
    response = client.get(url)

    assert response.status_code == 200
    assert "learning/topic_form.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_topic_create_view_post(client: Client) -> None:
    """Test TopicCreateView POST request creates a custom topic and redirects to essay creation."""
    url = reverse("learning:topic-create")
    post_data = {
        "title": "Nowy temat użytkownika",
        "description": "Szczegółowy opis nowego tematu."
    }
    response = client.post(url, post_data)

    assert Topic.objects.filter(title="Nowy temat użytkownika").exists()
    topic = Topic.objects.get(title="Nowy temat użytkownika")
    assert topic.is_custom is True
    assert topic.description == "Szczegółowy opis nowego tematu."

    expected_url = reverse("learning:essay-create", kwargs={"topic_id": topic.pk})
    assert response.status_code == 302
    assert response.url == expected_url


@pytest.mark.django_db
def test_feedback_detail_view(client: Client, sample_essay: Essay, mock_analysis_payload: Dict[str, Any]) -> None:
    """Test FeedbackDetailView displays evaluation feedback."""
    feedback = Feedback.objects.create(
        essay=sample_essay,
        corrected_text=mock_analysis_payload["corrected_text"],
        feedback_json=mock_analysis_payload
    )

    url = reverse("learning:feedback-detail", kwargs={"pk": feedback.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["feedback"] == feedback

