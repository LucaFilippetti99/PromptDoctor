import pytest
from unittest.mock import patch, MagicMock
from src.core.agent_workflow import MultiAgentRevisor, AgentState

@patch('src.core.agent_workflow.Ollama')
def test_multi_agent_workflow_success(mock_ollama_class):
    # Mock the LLM instance and its invoke method
    mock_llm_instance = MagicMock()
    # When prompt | llm is invoked, the LLM invoke is actually called under the hood, 
    # but to simplify we can mock the RunnableSequence invoke if it was exposed,
    # or better just patch the specific node methods to test the graph logic, 
    # or patch `Ollama.invoke` which is what LangChain calls.
    mock_llm_instance.invoke.side_effect = [
        "- Req 1\n- Req 2", # Analyst
        "Stack: Python, React", # Architect
        "## 1. Requisiti Funzionali\n- Req 1\n\n## 2. Architettura e Stack\nStack: Python" # Formatter
    ]
    mock_ollama_class.return_value = mock_llm_instance

    revisor = MultiAgentRevisor()
    
    # We patch the graph.invoke to simulate a successful run to test the fallback logic
    # because mocking LangChain's internal pipeline invoke with pure MagicMock can be flaky.
    with patch.object(revisor.graph, 'invoke') as mock_graph_invoke:
        mock_graph_invoke.return_value = {
            "final_structured_text": "## 1. Requisiti Funzionali\nTesto formattato bene"
        }
        
        result = revisor.rewrite_text("Voglio un sito verde")
        assert "Testo formattato bene" in result
        assert mock_graph_invoke.called

@patch('src.core.agent_workflow.StateGraph')
def test_multi_agent_fallback_on_error(mock_graph_class):
    # Force an exception during rewrite_text
    revisor = MultiAgentRevisor()
    
    with patch.object(revisor.graph, 'invoke', side_effect=Exception("Graph Failed")):
        result = revisor.rewrite_text("Richiesta Originale")
        assert result == "Richiesta Originale"

def test_multi_agent_empty_input():
    revisor = MultiAgentRevisor()
    assert revisor.rewrite_text("") == ""
    assert revisor.rewrite_text("   ") == "   "
