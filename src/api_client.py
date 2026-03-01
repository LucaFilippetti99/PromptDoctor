import requests
import streamlit as st

API_URL = "http://localhost:8000/api"

class PromptAPIClient:
    def analyze_text(self, problem_desc: str, use_ai: bool, custom_context: str = ""):
        """Chiama l'API per il pattern matching testuale live"""
        try:
            resp = requests.post(f"{API_URL}/analyze_text", json={
                "problem_desc": problem_desc,
                "use_ai": use_ai,
                "custom_context": custom_context
            })
            resp.raise_for_status()
            data = resp.json()
            return data.get("matches", []), data.get("modifiers", {}), data.get("used_ai", False)
        except Exception as e:
            # Fail silently to keep UX clean in case of backend drop
            return [], {}, False

    def generate_prompt(self, payload: dict) -> dict:
        """Chiama l'API per generare l'intero stack CO-STAR"""
        resp = requests.post(f"{API_URL}/generate_prompt", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_history(self) -> list:
        """Chiama l'API per lo storico dei prompt salvati"""
        try:
            resp = requests.get(f"{API_URL}/history")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return []
