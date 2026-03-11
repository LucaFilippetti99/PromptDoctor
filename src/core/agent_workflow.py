import json
import re
from typing import Dict, TypedDict
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langchain_core.callbacks import BaseCallbackHandler
from src.config import DEFAULT_MODEL, OLLAMA_API_URL, GEMINI_PROMPT_GUIDELINES

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Handler custom per lo streaming text-token su un componente Streamlit."""
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        # Aggiornamento fluido con il cursore lampeggiante ▌
        self.container.markdown(self.text + "▌")

class AgentState(TypedDict):
    original_request: str
    analysis: str
    architecture: str
    final_prompt: str
    score_ai: int
    giudizio_critico: str

class MultiAgentRevisor:
    """
    LangGraph-based workflow that orchestrates multiple AI agents 
    to restructure the user input.
    """
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_API_URL):
        # Extract the base URL for Ollama (e.g. http://localhost:11434)
        host = base_url.replace("/api/generate", "")
        self.llm = Ollama(model=model, base_url=host)
        
        # Build and compile the graph
        self.graph = self._build_graph()

    def _analyst_node(self, state: AgentState) -> Dict:
        """
        Analyzes the original request to extract functional requirements and actors.
        """
        prompt = PromptTemplate.from_template(
            "Sei un Technical Business Analyst. Analizza la seguente richiesta utente e deduci i requisiti "
            "funzionali, gli attori principali (chi usa il software) e gli scenari d'uso principali. "
            "Ignora i dettagli implementativi per ora e chiarisci le parti ambigue.\n"
            "Restituisci solo un elenco di requisiti chiari in Markdown. Non aggiungere saluti.\n\n"
            "Richiesta Utente:\n{request}"
        )
        chain = prompt | self.llm
        
        config = {}
        handler = None
        if hasattr(self, 'current_containers') and "analyst" in self.current_containers:
            handler = StreamlitCallbackHandler(self.current_containers["analyst"])
            config = {"callbacks": [handler]}
            
        result = chain.invoke({"request": state['original_request']}, config=config)
        
        if handler:
            handler.container.markdown(handler.text)
            
        return {"analysis": result.strip()}

    def _judge_node(self, state: AgentState) -> Dict:
        """
        Evaluates the original request, assigning a score and a critical analysis.
        """
        prompt = PromptTemplate.from_template(
            "Sei un Senior Prompt Engineer e un severo Giudice AI. Analizza la seguente richiesta utente. "
            "Valutane la qualità, la chiarezza e la completezza tenendo ESPLICITAMENTE CONTO delle seguenti "
            "LINEE GUIDA UFFICIALI (I 4 Elementi Fondamentali e le Regole d'Oro):\n"
            "{guidelines}\n\n"
            "Devi restituire esclusivamente un oggetto JSON valido con la seguente struttura:\n"
            '{{\n  "score": <intero da 0 a 100>,\n  "analisi": "<breve frase, max 15 parole>"\n}}\n'
            "L'analisi DEVE giustificare brevemente qual è l'elemento mancante o errato secondo le linee guida.\n"
            "Non includere marker markdown (es. ```json o ```). Solo il testo JSON.\n\n"
            "Richiesta Utente:\n{request}"
        )
        chain = prompt | self.llm
        
        config = {}
        
        try:
            result = chain.invoke({
                "request": state['original_request'],
                "guidelines": GEMINI_PROMPT_GUIDELINES
            }, config=config)
            
            # Utilizza regex per estrarre l'oggetto JSON per evitare errori di formato
            match = re.search(r'\{.*?\}', result, re.DOTALL)
            if match:
                clean_result = match.group(0)
                data = json.loads(clean_result)
                score_ai = int(data.get("score", 70))
                giudizio_critico = str(data.get("analisi", "L'intuizione è buona ma mancano dettagli."))
            else:
                raise ValueError("Nessun oggetto JSON trovato nella risposta dell'LLM.")
                
        except Exception as e:
            print(f"Error parsing AI Judge output: {e}\\nRaw output: {result if 'result' in locals() else 'N/A'}")
            score_ai = 70
            giudizio_critico = "Impossibile calcolare il punteggio automatico, assegnato 70 di default."
            
        return {"score_ai": score_ai, "giudizio_critico": giudizio_critico}

    def _architect_node(self, state: AgentState) -> Dict:
        """
        Proposes a high-level architecture and tech stack based on the analysis.
        """
        prompt = PromptTemplate.from_template(
            "Sei un Software Architect e Prompt Engineer. Basandoti sui seguenti requisiti funzionali, proponi "
            "un'architettura di alto livello e uno stack tecnologico adeguato. Spiega brevemente le scelte.\n"
            "Assicurati che l'architettura tenga conto delle seguenti LINEE GUIDA SUI PROMPT (se pertinenti "
            "per la stesura del codice/documentazione):\n{guidelines}\n\n"
            "Restituisci solo le scelte architetturali in Markdown. Non aggiungere saluti.\n\n"
            "Requisiti Funzionali:\n{analysis}"
        )
        chain = prompt | self.llm
        
        config = {}
        handler = None
        if hasattr(self, 'current_containers') and "architect" in self.current_containers:
            handler = StreamlitCallbackHandler(self.current_containers["architect"])
            config = {"callbacks": [handler]}
            
        result = chain.invoke({
            "analysis": state['analysis'],
            "guidelines": GEMINI_PROMPT_GUIDELINES
        }, config=config)
        
        if handler:
            handler.container.markdown(handler.text)
            
        return {"architecture": result.strip()}

    def _prompt_writer_node(self, state: AgentState) -> Dict:
        """
        Writes the final, polished prompt using Gemini Guidelines.
        Takes the analysis & architecture and produces a natural, 
        well-structured prompt ready to be copied by the user.
        """
        prompt = PromptTemplate.from_template(
            "Sei un Senior Prompt Engineer esperto in modelli Gemini e ChatGPT. "
            "Il tuo compito è scrivere il PROMPT PERFETTO e PRONTO ALL'USO basandoti sui dati qui sotto.\n\n"
            "RICHIESTA ORIGINALE DELL'UTENTE:\n{original_request}\n\n"
            "REQUISITI FUNZIONALI (estratti dall'Analista):\n{analysis}\n\n"
            "ARCHITETTURA E STACK (proposti dall'Architetto):\n{architecture}\n\n"
            "SEGUI RIGOROSAMENTE QUESTE LINEE GUIDA DI GEMINI PER SCRIVERE IL PROMPT:\n{guidelines}\n\n"
            "REGOLE DI SCRITTURA OBBLIGATORIE:\n"
            "1. Assegna un RUOLO chiaro all'IA (es. 'Sei un esperto di...').\n"
            "2. Descrivi l'ATTIVITÀ con verbi d'azione precisi.\n"
            "3. Fornisci CONTESTO ricco e specifico (tecnologie, vincoli, pubblico target).\n"
            "4. Specifica il FORMATO di output desiderato (codice, markdown, tabella, ecc.).\n"
            "5. Usa un linguaggio naturale e discorsivo, come se parlassi a un collega.\n"
            "6. Sii conciso ma completo: mira a circa 150-300 parole.\n"
            "7. Concludi chiedendo: 'C'è qualche informazione aggiuntiva che ti sarebbe utile per generare un output ottimale?'\n\n"
            "Restituisci SOLO il testo del prompt finale. Nessun commento, nessun saluto, nessuna introduzione."
        )
        chain = prompt | self.llm

        config = {}
        handler = None
        if hasattr(self, 'current_containers') and "prompt_writer" in self.current_containers:
            handler = StreamlitCallbackHandler(self.current_containers["prompt_writer"])
            config = {"callbacks": [handler]}

        result = chain.invoke({
            "original_request": state['original_request'],
            "analysis": state['analysis'],
            "architecture": state['architecture'],
            "guidelines": GEMINI_PROMPT_GUIDELINES
        }, config=config)

        if handler:
            handler.container.markdown(handler.text)

        return {"final_prompt": result.strip()}

    def _build_graph(self):
        """
        Constructs the state machine / agent graph.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("judge", self._judge_node)
        workflow.add_node("analyst", self._analyst_node)
        workflow.add_node("architect", self._architect_node)
        workflow.add_node("prompt_writer", self._prompt_writer_node)
        
        # Add edges connecting the nodes
        workflow.set_entry_point("judge")
        workflow.add_edge("judge", "analyst")
        workflow.add_edge("analyst", "architect")
        workflow.add_edge("architect", "prompt_writer")
        workflow.add_edge("prompt_writer", END)
        
        # Compile the graph
        return workflow.compile()

    def rewrite_text(self, text: str, containers: Dict = None) -> Dict:
        """
        Executes the Multi-Agent workflow on the input text.
        Returns a dictionary with text, score_ai, and giudizio_critico.
        """
        self.current_containers = containers or {}
        
        fallback = {
            "text": text,
            "score_ai": 70,
            "giudizio_critico": "Analisi non completata."
        }
        
        if not text or not text.strip():
            return fallback
            
        try:
            initial_state = {
                "original_request": text,
                "analysis": "",
                "architecture": "",
                "final_prompt": "",
                "score_ai": 0,
                "giudizio_critico": ""
            }
            
            # Execute the graph
            result = self.graph.invoke(initial_state)
            
            # Extract final prompt written by the Prompt Writer agent
            final_prompt = result.get('final_prompt', "").strip()
            # Keep the structured text for backward compat
            analysis = result.get('analysis', "").strip()
            architecture = result.get('architecture', "").strip()
            score_ai = result.get('score_ai', 70)
            giudizio_critico = result.get('giudizio_critico', "Analisi completata con successo.")
            
            if not final_prompt:
                return fallback
                
            return {
                "text": final_prompt,
                "final_prompt": final_prompt,
                "analysis": analysis,
                "architecture": architecture,
                "score_ai": score_ai,
                "giudizio_critico": giudizio_critico
            }
            
        except Exception as e:
            print(f"Error during LangGraph Execution: {e}")
            return fallback
