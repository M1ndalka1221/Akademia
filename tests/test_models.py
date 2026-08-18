"""Unit tests for the learning models in Akademia."""

import pytest
from learning.models import Topic, Essay, Feedback, Vocabulary


@pytest.mark.django_db
def test_topic_creation_and_str() -> None:
    """Test Topic model instantiation and __str__ representation."""
    topic = Topic.objects.create(
        title="Moje ulubione hobby",
        description="Opisz swoje ulubione zajęcie w czasie wolnym."
    )
    assert topic.pk is not None
    assert str(topic) == "Moje ulubione hobby"


@pytest.mark.django_db
def test_essay_creation_and_str() -> None:
    """Test Essay model creation and string representation."""
    topic = Topic.objects.create(
        title="Wakacje w Polsce",
        description="Opisz swoją podróż do Krakowa."
    )
    essay = Essay.objects.create(
        topic=topic,
        content="Bardzo lubię podróżować po Polsce."
    )
    assert essay.pk is not None
    assert essay.topic == topic
    assert "Essay on 'Wakacje w Polsce'" in str(essay)


@pytest.mark.django_db
def test_feedback_creation_and_str() -> None:
    """Test Feedback model creation and relation to Essay."""
    topic = Topic.objects.create(title="Środowisko")
    essay = Essay.objects.create(topic=topic, content="Ochrona przyrody jest ważna.")
    
    feedback_data = {
        "errors": [
            {"original": "przyrody", "suggestion": "środowiska", "explanation": "Grammar check"}
        ],
        "synonyms": [
            {"word": "ważna", "advanced": "kluczowa"}
        ]
    }
    
    feedback = Feedback.objects.create(
        essay=essay,
        corrected_text="Ochrona środowiska jest kluczowa.",
        feedback_json=feedback_data
    )
    
    assert feedback.pk is not None
    assert feedback.essay == essay
    assert str(feedback) == f"Feedback for Essay #{essay.pk}"
    assert feedback.feedback_json["errors"][0]["suggestion"] == "środowiska"


@pytest.mark.django_db
def test_vocabulary_creation_and_str() -> None:
    """Test Vocabulary model creation and __str__ output."""
    vocab = Vocabulary.objects.create(
        word="wyzwanie",
        translation="challenge",
        example_sentence="To nowe zadanie to duże wyzwanie."
    )
    assert vocab.pk is not None
    assert str(vocab) == "wyzwanie - challenge"


@pytest.mark.django_db
def test_topic_and_essay_user_association(django_user_model) -> None:
    """Test associating a user with Topic and Essay models."""
    user = django_user_model.objects.create_user(
        username="jan_kowalski",
        email="jan@example.com",
        password="secretpassword"
    )
    topic = Topic.objects.create(
        user=user,
        title="Własny temat użytkownika",
        is_custom=True
    )
    essay = Essay.objects.create(
        user=user,
        topic=topic,
        content="Przykładowa treść eseju napisanego przez użytkownika."
    )
    assert topic.user == user
    assert essay.user == user
    assert essay in user.essays.all()
    assert topic in user.topics.all()

