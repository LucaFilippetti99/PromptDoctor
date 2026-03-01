import pytest
from unittest.mock import patch, MagicMock
from src.core.rewriter import AIRevisor

@patch('src.core.rewriter.requests.post')
def test_ai_revisor_success(mock_post):
    # Setup mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "# Step 1: Login\n# Step 2: Tabella Utenti"
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    # Test
    revisor = AIRevisor(ollama_url="http://fake-test-url/api/generate", model="test-model")
    result = revisor.rewrite_text("Voglio un sito che fa il login poi deve avere una tabella")

    # Assert
    assert "Step 1: Login" in result
    assert "Step 2: Tabella Utenti" in result
    assert mock_post.called

@patch('src.core.rewriter.requests.post')
def test_ai_revisor_fallback_on_error(mock_post):
    # Setup mock to raise Exception
    mock_post.side_effect = Exception("API down")

    # Test
    revisor = AIRevisor(ollama_url="http://fake-test-url/api/generate", model="test-model")
    original_text = "Voglio un sito"
    result = revisor.rewrite_text(original_text)

    # Assert fallback to original text
    assert result == original_text
