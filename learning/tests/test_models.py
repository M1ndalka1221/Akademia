"""Unit tests for learning application models."""

import pytest
from learning.models import Essay, Feedback, Topic, Vocabulary


@pytest.mark.django_db
def test_topic_model(sample_topic: Topic) -> None:
    """Test Topic model attributes and string representation."""
    assert sample_topic.pk is not None
    assert sample_topic.title == "Przyszłość sztucznej inteligencji"
    assert str(sample_topic) == "Przyszłość sztucznej inteligencji"


@pytest.mark.django_db
def test_essay_model(sample_essay: Essay, sample_topic: Topic) -> None:
    """Test Essay model relationship with Topic and string representation."""
    assert sample_essay.pk is not None
    assert sample_essay.topic == sample_topic
    assert "Essay on 'Przyszłość sztucznej inteligencji'" in str(sample_essay)


@pytest.mark.django_db
def test_feedback_model(sample_essay: Essay) -> None:
    """Test Feedback model creation linked to Essay and string representation."""
    feedback = Feedback.objects.create(
        essay=sample_essay,
        corrected_text="Poprawiona treść eseju.",
        feedback_json={"errors": ["Brak błędu"], "advanced_synonyms": []}
    )
    assert feedback.pk is not None
    assert feedback.essay == sample_essay
    assert str(feedback) == f"Feedback for Essay #{sample_essay.pk}"


@pytest.mark.django_db
def test_vocabulary_model() -> None:
    """Test Vocabulary model attributes and string representation."""
    vocab = Vocabulary.objects.create(
        word="spostrzeżenie",
        translation="observation / insight",
        example_sentence="Jego spostrzeżenia były trafne."
    )
    assert vocab.pk is not None
    assert vocab.word == "spostrzeżenie"
    assert str(vocab) == "spostrzeżenie - observation / insight"
