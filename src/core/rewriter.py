import requests
import json
from src.config import OLLAMA_API_URL, DEFAULT_MODEL

class AIRevisor:
    """
    Engine for rewriting and structuring raw user text into 
    clear, actionable steps and logical blocks.
    """
    
    def __init__(self, ollama_url: str = OLLAMA_API_URL, model: str = DEFAULT_MODEL):
        self.ollama_url = ollama_url
        self.model = model

    def rewrite_text(self, text: str) -> str:
        """
        Takes raw, unstructured user input and uses the local LLM to 
        rewrite it clearly, dividing it into steps and logical components.
        Returns the structured text.
        """
        prompt = f"""
        Sei un formidabile technical business analyst e software architect.
        Il tuo compito è prendere la seguente richiesta di un utente, che potrebbe essere 
        scritta male, essere molto confusa, o mancare di struttura logica, e trasformarla
        in una specifica chiara e professionale.
        
        REGOLE FONDAMENTALI:
        1. Dividi la logica in step cronologici chiari e operativi.
        2. Raggruppa le specifiche in categorie funzionali (es. Interfaccia Utente, Logica di Business, Dati/Database).
        3. Identifica e risolvi eventuali ambiguità deducendo le best practice ovvie (es. se chiede un sito verde e nero, mettilo sotto 'Requisiti UI/UX').
        4. NON inserire saluti, convenevoli o note introduttive ("Ecco la tua richiesta...").
        5. Restituisci ESCLUSIVAMENTE il contenuto strutturato in formato Markdown leggibile e ben spaziato.
        6. Rispondi in Italiano in modo professionale, tecnico ma chiaro.

        Richiesta Utente Base: 
        "{text}"
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=25)
            response.raise_for_status()
            result = response.json()
            response_text = result.get('response', '').strip()
            
            # Fallback if the response is empty
            if not response_text:
                return text
                
            return response_text
            
        except Exception as e:
            # Fallback to original text on any error
            print(f"Error during AI Rewriting: {e}")
            return text
