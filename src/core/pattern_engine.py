import re
import json
import requests
from typing import Tuple, Dict, Any, List
from src.config import STATIC_TECH_PATTERNS, OLLAMA_API_URL, DEFAULT_MODEL

class PatternEngine:
    """
    Engine for extracting tech patterns from user input.
    Supports both static Regex-based rules and dynamic LLM (Local Ollama) detection.
    """
    
    def __init__(self, ollama_url: str = OLLAMA_API_URL, model: str = DEFAULT_MODEL):
        self.ollama_url = ollama_url
        self.model = model

    def analyze_text(self, text: str, use_ai: bool = False) -> Tuple[List[str], Dict[str, Any], bool]:
        """
        Analyze text and extract patterns.
        Returns: (matches, modifiers, used_ai)
        """
        if use_ai:
            ai_matches, ai_modifiers = self._ai_analysis(text)
            if ai_matches or ai_modifiers.get('libs') or ai_modifiers.get('framework'):
                return ai_matches, ai_modifiers, True
            # Fallback if AI fails or returns empty
        
        static_matches, static_modifiers = self._static_analysis(text)
        return static_matches, static_modifiers, False

    def _static_analysis(self, text: str) -> Tuple[List[str], Dict[str, Any]]:
        matches = []
        modifiers = {
            'libs': set(),
            'framework': set(),
            'prefix': '',
            'api': set(),
            'ui': set(),
            'platform': set(),
            'data': set(),
            'iterative': False
        }
        
        for pattern, data in STATIC_TECH_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Clean up the regex pattern for display
                display_name = pattern.replace('(', '').replace(')', '').split('|')[0]
                matches.append(display_name)
                
                for k, v in data.items():
                    if k == 'libs':
                        modifiers['libs'].update(v.split())
                    elif k == 'framework':
                        modifiers['framework'].add(v)
                    elif k == 'prefix':
                        modifiers['prefix'] = v
                    elif k == 'api':
                        modifiers['api'].add(v)
                    elif k == 'ui':
                        modifiers['ui'].update(v.split())
                    elif k == 'platform':
                        modifiers['platform'].update(v.split())
                    elif k == 'data':
                        modifiers['data'].update(v.split())
                    elif k == 'iterative':
                        modifiers['iterative'] = True
                        
        return matches, modifiers

    def _ai_analysis(self, text: str) -> Tuple[List[str], Dict[str, Any]]:
        prompt = f"""
        Sei un software architect. Analizza la seguente richiesta di progetto e identifica le tecnologie chiave rilevanti.
        Restituisci ESATTAMENTE e SOLO un JSON valido con questa struttura. Non includere backtick o markdown extra.

        {{
            "patterns": ["lista di concetti o feature rilevanti, es: barcode scanner, magic deck, data analysis"],
            "libs": ["lista di librerie Python o JS suggerite, es: pyzbar, opencv-python, pandas"],
            "framework": ["framework suggerito, es: streamlit, fastapi"],
            "api": ["api suggerite da integrare, es: scryfall, spoonacular"],
            "iterative": false // true se l'utente chiede di modificare, aggiornare o fixare codice esistente
        }}

        Richiesta: "{text}"
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            response_text = result.get('response', '{}')
            
            data = json.loads(response_text)
            
            matches = data.get('patterns', [])
            modifiers = {
                'libs': set(data.get('libs', [])),
                'framework': set(data.get('framework', [])),
                'prefix': '**CONTINUA DAL CODICE PRECEDENTE**\n**MODIFICA:**' if data.get('iterative', False) else '',
                'api': set(data.get('api', [])),
                'ui': set(),
                'platform': set(),
                'data': set(),
                'iterative': data.get('iterative', False)
            }
            return matches, modifiers
            
        except Exception as e:
            # Silently fallback
            return [], {}
