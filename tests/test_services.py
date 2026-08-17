"""Unit tests for services layer in Akademia (LLMAnalyzer)."""

from unittest.mock import MagicMock, patch
import pytest
from services.llm_analyzer import LLMAnalyzer, LLMAnalysisError


def test_analyze_essay_success() -> None:
    """Test successful essay analysis with mocked Gemini API response."""
    mock_json_response = """
    {
        "corrected_text": "Bardzo lubię podróżować po Polsce.",
        "errors": [
            "Brak przecinka przed spojnikiem 'że' w poprzednim zdaniu."
        ],
        "advanced_synonyms": [
            {
                "original": "lubię",
                "suggestion": "uwielbiam / mam zamiłowanie do",
                "explanation": "Podnosi poziom stylistyczny wypowiedzi."
            }
        ]
    }
    """
    
    analyzer = LLMAnalyzer(api_key="test_api_key")
    
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = mock_json_response
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model_instance
        
        result = analyzer.analyze_essay("Bardzo lubie podrozowac po polsce.")
        
        assert "corrected_text" in result
        assert result["corrected_text"] == "Bardzo lubię podróżować po Polsce."
        assert len(result["errors"]) == 1
        assert len(result["advanced_synonyms"]) == 1
        assert result["advanced_synonyms"][0]["original"] == "lubię"


def test_analyze_essay_empty_input_raises_error() -> None:
    """Test that empty or whitespace-only essay raises LLMAnalysisError."""
    analyzer = LLMAnalyzer(api_key="test_api_key")
    with pytest.raises(LLMAnalysisError, match="Treść eseju nie może być pusta"):
        analyzer.analyze_essay("   ")


def test_analyze_essay_missing_api_key_raises_error() -> None:
    """Test that missing API key raises LLMAnalysisError."""
    analyzer = LLMAnalyzer(api_key="")
    with pytest.raises(LLMAnalysisError, match="Brak skonfigurowanego klucza"):
        analyzer.analyze_essay("Moje ulubione hobby to czytanie książek.")


def test_analyze_essay_invalid_json_raises_error() -> None:
    """Test that invalid JSON from Gemini raises LLMAnalysisError."""
    analyzer = LLMAnalyzer(api_key="test_api_key")
    
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not a JSON output!"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model_instance
        
        with pytest.raises(LLMAnalysisError, match="Błędny format odpowiedzi JSON"):
            analyzer.analyze_essay("Przykładowy esej.")


def test_analyze_essay_missing_keys_raises_error() -> None:
    """Test that JSON response missing required keys raises LLMAnalysisError."""
    analyzer = LLMAnalyzer(api_key="test_api_key")
    
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"corrected_text": "Text without errors key"}'
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model_instance
        
        with pytest.raises(LLMAnalysisError, match="Odpowiedź LLM nie zawiera wymaganych kluczy"):
            analyzer.analyze_essay("Przykładowy esej.")


def test_analyze_essay_api_exception_handling() -> None:
    """Test handling when Gemini API raises an exception."""
    analyzer = LLMAnalyzer(api_key="test_api_key")
    
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("Quota exceeded")
        mock_model_cls.return_value = mock_model_instance
        
        with pytest.raises(LLMAnalysisError, match="Błąd analizy Gemini API"):
            analyzer.analyze_essay("Przykładowy esej.")
