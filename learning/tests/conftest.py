"""Pytest fixtures for the learning application tests."""

from typing import Any, Dict
import pytest
from learning.models import Essay, Topic


@pytest.fixture
def sample_topic(db: Any) -> Topic:
    """Fixture to create a sample Topic object."""
    return Topic.objects.create(
        title="Przyszłość sztucznej inteligencji",
        description="Rozważ wpływy i szanse rozwoju technologii AI w społeczeństwie."
    )


@pytest.fixture
def sample_essay(db: Any, sample_topic: Topic) -> Essay:
    """Fixture to create a sample Essay object associated with sample_topic."""
    return Essay.objects.create(
        topic=sample_topic,
        content="Sztuczna inteligencja rozwija się bardzo szybko i zmienia nasz świat."
    )


@pytest.fixture
def mock_analysis_payload() -> Dict[str, Any]:
    """Fixture providing a predefined LLM analysis JSON response."""
    return {
        "corrected_text": "Sztuczna inteligencja rozwija się dynamicznie i przekształca nasz świat.",
        "errors": [
            "Użyto potocznego zwrotu 'bardzo szybko' - lepiej użyć 'dynamicznie'."
        ],
        "advanced_synonyms": [
            {
                "original": "bardzo szybko",
                "suggestion": "dynamicznie / gwałtownie",
                "explanation": "Podnosi rejestr stylistyczny wypowiedzi na poziom C1."
            },
            {
                "original": "zmienia",
                "suggestion": "przekształca / rewolucjonizuje",
                "explanation": "Wyrazistszy czasownik używany w tekstach naukowych."
            }
        ]
    }
