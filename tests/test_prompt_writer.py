"""Test script to verify the Prompt Writer Agent integration."""
import requests
import time

API_URL = "http://127.0.0.1:8000/api/generate_prompt"

# ---------- TEST 1: use_ai=True (Prompt Writer AI) ----------
print("=" * 60)
print("TEST 1: use_ai=True (Prompt Writer AI)")
print("=" * 60)

payload_ai = {
    "problem_desc": "Voglio un sito in HTML che mostri il mio curriculum vitae",
    "obiettivo": "Sito Web Curriculum",
    "ruolo": "Sviluppatore web frontend",
    "framework": "HTML",
    "lingua": "Italiano",
    "dettaglio": 50,
    "is_iterativo": False,
    "use_ai": True,
    "custom_context": ""
}

try:
    response = requests.post(API_URL, json=payload_ai, timeout=300)
    if response.status_code == 200:
        data = response.json()
        print("Score AI:", data.get("score_ai"))
        print("Giudizio Critico:", data.get("giudizio_critico"))
        print("Used AI Prompt:", data.get("used_ai_prompt"))
        print("-" * 40)
        print("PROMPT GENERATO DAL PROMPT WRITER:")
        print(data.get("final_prompt", "VUOTO")[:500])
        print("..." if len(data.get("final_prompt", "")) > 500 else "")
    else:
        print("ERRORE:", response.status_code, response.text[:300])
except Exception as e:
    print("Errore di connessione:", e)

print()

# ---------- TEST 2: use_ai=False (CO-STAR Fallback) ----------
print("=" * 60)
print("TEST 2: use_ai=False (CO-STAR Fallback)")
print("=" * 60)

payload_costar = {
    "problem_desc": "Voglio un sito in HTML che mostri il mio curriculum vitae",
    "obiettivo": "Sito Web Curriculum",
    "ruolo": "Sviluppatore web frontend",
    "framework": "HTML",
    "lingua": "Italiano",
    "dettaglio": 50,
    "is_iterativo": False,
    "use_ai": False,
    "custom_context": ""
}

try:
    response = requests.post(API_URL, json=payload_costar, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print("Used AI Prompt:", data.get("used_ai_prompt"))
        print("-" * 40)
        print("PROMPT CO-STAR GENERATO:")
        print(data.get("final_prompt", "VUOTO")[:500])
    else:
        print("ERRORE:", response.status_code, response.text[:300])
except Exception as e:
    print("Errore di connessione:", e)
