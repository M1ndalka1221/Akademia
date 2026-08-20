"""Unit tests for Interactive Flashcards ("Fiszki C1") view and URL routing."""

import json
import pytest
from django.urls import reverse

from learning.models import Vocabulary


@pytest.mark.django_db
def test_flashcard_list_view_get(client) -> None:
    """Test FlashcardView GET request renders successfully with serialized JSON data."""
    v1 = Vocabulary.objects.create(
        word="błyskotliwość",
        translation="остроумие",
        example_sentence="Błyskotliwość w dyskusji.",
        is_custom=False
    )
    v2 = Vocabulary.objects.create(
        word="dociekliwość",
        translation="пытливость",
        example_sentence="Dziennikarska dociekliwość.",
        is_custom=True
    )

    url = reverse("learning:flashcard-list")
    response = client.get(url)

    assert response.status_code == 200
    assert "learning/flashcard_list.html" in [t.name for t in response.templates]
    assert "vocab_json" in response.context
    assert response.context["vocab_count"] >= 2

    # Verify JSON deserialization contains created terms
    items = json.loads(response.context["vocab_json"])
    words = [item["word"] for item in items]
    assert "błyskotliwość" in words
    assert "dociekliwość" in words


@pytest.mark.django_db
def test_flashcard_list_view_filtering(client) -> None:
    """Test filtering flashcard deck by source parameter (ai vs custom)."""
    ai_item = Vocabulary.objects.create(
        word="unikatowe_slowo_ai_123",
        translation="сложность",
        is_custom=False
    )
    custom_item = Vocabulary.objects.create(
        word="unikatowe_slowo_custom_456",
        translation="сожалеть",
        is_custom=True
    )

    url = reverse("learning:flashcard-list")

    # Filter by source=ai
    ai_res = client.get(f"{url}?source=ai")
    assert ai_res.status_code == 200
    ai_items = json.loads(ai_res.context["vocab_json"])
    ai_words = [i["word"] for i in ai_items]
    assert "unikatowe_slowo_ai_123" in ai_words
    assert "unikatowe_slowo_custom_456" not in ai_words

    # Filter by source=custom
    custom_res = client.get(f"{url}?source=custom")
    assert custom_res.status_code == 200
    custom_items = json.loads(custom_res.context["vocab_json"])
    custom_words = [i["word"] for i in custom_items]
    assert "unikatowe_slowo_custom_456" in custom_words
    assert "unikatowe_slowo_ai_123" not in custom_words

