import os
import sys
import pytest

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pattern_engine import PatternEngine

def test_static_pattern_detection():
    engine = PatternEngine()
    
    # Test barcode pattern
    text = "Voglio un barcode scanner per la mia app"
    matches, modifiers, used_ai = engine.analyze_text(text, use_ai=False)
    
    assert used_ai is False
    assert any("barcode" in m.lower() for m in matches)
    assert "treepoem" in modifiers['libs']
    assert "streamlit" in modifiers['framework']

def test_iterator_pattern():
    engine = PatternEngine()
    
    # Test iterative modification
    text = "Modifica il codice esistente"
    matches, modifiers, used_ai = engine.analyze_text(text, use_ai=False)
    
    assert used_ai is False
    assert modifiers['iterative'] is True
    assert "**CONTINUA DAL CODICE PRECEDENTE**" in modifiers['prefix']

def test_no_pattern():
    engine = PatternEngine()
    
    # Test text without technical patterns
    text = "Voglio un programma che faccia cose bellissime e basta."
    matches, modifiers, used_ai = engine.analyze_text(text, use_ai=False)
    
    assert len(matches) == 0
    assert not modifiers['libs']
