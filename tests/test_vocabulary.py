"""Unit tests for Vocabulary views, forms, and Gemini generator service."""

from unittest.mock import MagicMock, patch
import pytest
from django.test import override_settings
from django.urls import reverse

from learning.models import Vocabulary
from learning.forms import VocabularyForm
from services.llm_analyzer import LLMAnalysisError, LLMAnalyzer


@pytest.mark.django_db
def test_vocabulary_list_view_get(client) -> None:
    """Test VocabularyListView renders successfully with vocabulary list."""
    vocab1 = Vocabulary.objects.create(
        word="dociekliwość",
        translation="пытливость",
        example_sentence="Jego dociekliwość była godna podziwu.",
        is_custom=False
    )
    vocab2 = Vocabulary.objects.create(
        word="błyskotliwość",
        translation="остроумие",
        example_sentence="Błyskotliwość wypowiedzi.",
        is_custom=True
    )

    url = reverse("learning:vocabulary-list")
    response = client.get(url)

    assert response.status_code == 200
    assert "learning/vocabulary_list.html" in [t.name for t in response.templates]
    assert vocab1 in response.context["vocabularies"]
    assert vocab2 in response.context["vocabularies"]


@pytest.mark.django_db
def test_vocabulary_list_view_search_and_filter(client) -> None:
    """Test filtering vocabulary by search query and source (ai/custom)."""
    ai_word = Vocabulary.objects.create(
        word="zawiłość",
        translation="сложность",
        is_custom=False
    )
    custom_word = Vocabulary.objects.create(
        word="ubolewać",
        translation="сожалеть",
        is_custom=True
    )

    url = reverse("learning:vocabulary-list")
    
    # Filter by source=ai
    ai_res = client.get(f"{url}?source=ai")
    assert ai_res.status_code == 200
    assert ai_word in ai_res.context["vocabularies"]
    assert custom_word not in ai_res.context["vocabularies"]

    # Filter by search q=ubolewać
    search_res = client.get(f"{url}?q=ubolewać")
    assert search_res.status_code == 200
    assert custom_word in search_res.context["vocabularies"]
    assert ai_word not in search_res.context["vocabularies"]


@pytest.mark.django_db
def test_vocabulary_create_view(client) -> None:
    """Test VocabularyCreateView GET and valid POST submission."""
    url = reverse("learning:vocabulary-create")

    # GET
    get_res = client.get(url)
    assert get_res.status_code == 200
    assert "learning/vocabulary_form.html" in [t.name for t in get_res.templates]

    # POST
    post_data = {
        "word": "rozwiać wątpliwości",
        "translation": "развеять сомнения",
        "example_sentence": "Dowody rozwiały wątpliwości."
    }
    post_res = client.post(url, post_data)
    assert post_res.status_code == 302
    assert Vocabulary.objects.filter(word="rozwiać wątpliwości", is_custom=True).exists()


@pytest.mark.django_db
def test_vocabulary_generate_ai_view(client) -> None:
    """Test triggering Gemini AI vocabulary generation creates DB items."""
    url = reverse("learning:vocabulary-generate")

    mock_items = [
        {
            "word": "skrupulatność",
            "translation": "скрупулезность",
            "example_sentence": "Skrupulatność w pracy."
        }
    ]

    with patch("learning.views.LLMAnalyzer") as mock_analyzer_cls:
        mock_instance = MagicMock()
        mock_instance.generate_c1_vocabulary.return_value = mock_items
        mock_analyzer_cls.return_value = mock_instance

        response = client.get(url)
        assert response.status_code == 302
        assert Vocabulary.objects.filter(word="skrupulatność", is_custom=False).exists()


@pytest.mark.django_db
def test_vocabulary_delete_view(client) -> None:
    """Test VocabularyDeleteView deletes custom word."""
    vocab = Vocabulary.objects.create(
        word="do_usunięcia",
        translation="к удалению",
        is_custom=True
    )
    url = reverse("learning:vocabulary-delete", kwargs={"pk": vocab.pk})
    
    response = client.post(url)
    assert response.status_code == 302
    assert not Vocabulary.objects.filter(pk=vocab.pk).exists()


@override_settings(DEBUG=True)
def test_llm_analyzer_generate_c1_vocabulary_demo_fallback() -> None:
    """Test LLMAnalyzer generate_c1_vocabulary demo fallback when API key is missing."""
    analyzer = LLMAnalyzer(api_key="")
    # Should generate demo items in DEBUG mode
    items = analyzer.generate_c1_vocabulary(count=3)
    assert isinstance(items, list)
    assert len(items) > 0
    assert "word" in items[0]
    assert "translation" in items[0]


