# PromptDoctor — Documentazione Tecnica Completa

> Una panoramica approfondita dell'architettura, del tech stack e dei framework utilizzati nel progetto PromptDoctor.

---

## Indice

1. [Panoramica del Progetto](#1-panoramica-del-progetto)
2. [Struttura delle Directory](#2-struttura-delle-directory)
3. [Tech Stack — Mappa Rapida](#3-tech-stack--mappa-rapida)
4. [Architettura Client-Server](#4-architettura-client-server)
5. [Frontend: Streamlit](#5-frontend-streamlit)
6. [Backend: FastAPI + Uvicorn](#6-backend-fastapi--uvicorn)
7. [AI Engine: Ollama + LangChain + LangGraph](#7-ai-engine-ollama--langchain--langgraph)
8. [Pattern Engine (Doppio Motore)](#8-pattern-engine-doppio-motore)
9. [Multi-Agent Workflow](#9-multi-agent-workflow)
10. [Generazione Prompt CO-STAR](#10-generazione-prompt-co-star)
11. [Sistema di Score e Gamification](#11-sistema-di-score-e-gamification)
12. [Database: SQLite3 (DAO Pattern)](#12-database-sqlite3-dao-pattern)
13. [Comunicazione HTTP: api_client.py](#13-comunicazione-http-api_clientpy)
14. [UI Components e Stile](#14-ui-components-e-stile)
15. [Flusso Dati End-to-End](#15-flusso-dati-end-to-end)
16. [Pattern Architetturali Usati](#16-pattern-architetturali-usati)
17. [Test Suite](#17-test-suite)
18. [Dipendenze e Versioni](#18-dipendenze-e-versioni)
19. [Come Avviare il Progetto](#19-come-avviare-il-progetto)

---

## 1. Panoramica del Progetto

**PromptDoctor** è un'applicazione web locale che aiuta gli sviluppatori a generare prompt di alta qualità per AI assistant. Combina:

- Un'interfaccia web interattiva costruita con **Streamlit**
- Un backend REST costruito con **FastAPI**
- Un motore di pattern matching ibrido (regex + AI semantica)
- Un workflow multi-agente con **LangGraph** (Judge → Analyst → Architect → Prompt Writer)
- Un generatore di prompt strutturati secondo il framework **CO-STAR**
- Un sistema di gamification con scoring multi-dimensionale
- Persistenza locale tramite **SQLite3**
- Un LLM locale tramite **Ollama** (nessun dato inviato al cloud)

L'intero stack gira in locale: privacy-first, senza dipendenze da API cloud.

---

## 2. Struttura delle Directory

```
PromptDoctor/
│
├── src/                          # Sorgente principale
│   ├── core/                     # Logica business core
│   │   ├── pattern_engine.py     # Motore pattern matching (regex + LLM)
│   │   ├── agent_workflow.py     # Workflow multi-agent con LangGraph
│   │   ├── rewriter.py           # Revisore AI (testo libero)
│   │   └── db_manager.py         # Data Access Object per SQLite
│   │
│   ├── ui/                       # Componenti UI Streamlit
│   │   └── components.py         # Sidebar, badge, score card
│   │
│   ├── utils/                    # Utility e helper
│   │   └── score.py              # Calcolo score gamificato
│   │
│   ├── app.py                    # Entry point frontend (Streamlit)
│   ├── api_server.py             # Entry point backend (FastAPI)
│   ├── api_client.py             # Client HTTP (frontend → backend)
│   ├── config.py                 # CSS, pattern statici, costanti
│   └── prompt_generator.py       # Builder CO-STAR
│
├── tests/                        # Test suite
│   ├── test_pattern_engine.py
│   ├── test_agent_workflow.py
│   ├── test_rewriter.py
│   └── test_prompt_writer.py
│
├── run.py                        # Launcher unico (avvia entrambi i processi)
├── requirements.txt              # Dipendenze Python
├── setup.sh / setup.bat          # Script di setup virtualenv
├── README.md                     # Documentazione utente
├── prompts_history.db            # Database SQLite (generato a runtime)
└── .streamlit/                   # Configurazione opzionale Streamlit
```

---

## 3. Tech Stack — Mappa Rapida

| Layer | Tecnologia | Versione | Scopo |
|---|---|---|---|
| Frontend UI | **Streamlit** | >=1.30.0 | Interfaccia web interattiva |
| HTTP Client | **Requests** | >=2.31.0 | Chiamate REST frontend→backend e backend→Ollama |
| Data Display | **Pandas** | >=2.0.0 | Tabelle CO-STAR breakdown |
| Backend REST | **FastAPI** | (da venv) | Framework API ad alte prestazioni |
| ASGI Server | **Uvicorn** | (da venv) | Serve FastAPI in produzione/dev |
| Data Validation | **Pydantic** | (da venv) | Validazione input/output API |
| LLM Locale | **Ollama** | >=0.1.6 | Inference LLM locale (llama3.2) |
| AI Orchestration | **LangChain** | (da venv) | Catene LLM, PromptTemplate |
| Multi-Agent | **LangGraph** | (da venv) | DAG di agenti sequenziali |
| Database | **SQLite3** | built-in Python | Storage leggero embedded |
| ML Framework | **Transformers** | >=4.37.0 | Dipendenza transitiva HuggingFace |
| ML Runtime | **PyTorch** | >=2.1.0 | Dipendenza transitiva Transformers |
| Testing | **Pytest** | >=8.0.0 | Unit e integration test |

---

## 4. Architettura Client-Server

PromptDoctor adotta una separazione netta tra frontend e backend comunicanti via HTTP REST.

```
┌──────────────────────────────────────────────────────────────────┐
│                STREAMLIT FRONTEND  :8501                         │
│                      src/app.py                                  │
│                                                                  │
│  Sidebar ──────── Text area ────── Badge ────── Score Card      │
│  (componenti)     (problema)        (pattern)    (gamification)  │
└─────────────────────────┬────────────────────────────────────────┘
                          │  HTTP REST (requests)
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                FASTAPI BACKEND  :8000                            │
│                   src/api_server.py                              │
│                                                                  │
│  POST /api/analyze_text   ──►  PatternEngine                    │
│  POST /api/generate_prompt ──► PatternEngine + MultiAgent +     │
│                                generate_costar + score + DB     │
│  GET  /api/history        ──►  PromptDBManager                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │  HTTP localhost:11434
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│               OLLAMA LOCAL LLM SERVER  :11434                    │
│                     Model: llama3.2                              │
│                                                                  │
│  Pattern analysis (JSON format)                                  │
│  Judge / Analyst / Architect / Prompt Writer nodes               │
└──────────────────────────┬───────────────────────────────────────┘
                           │  File system
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                SQLite  prompts_history.db                        │
│    id | timestamp | original_input | generated_prompt | score   │
└──────────────────────────────────────────────────────────────────┘
```

**Perché questa separazione?**

- Il frontend Streamlit è stateless lato server: ogni interazione utente è un rerun del codice Python. Separare la business logic in un backend FastAPI evita di re-istanziare l'LLM e il DB ad ogni rerun.
- I singleton (PatternEngine, MultiAgentRevisor, PromptDBManager) vengono creati una sola volta all'avvio del server FastAPI e rimangono in memoria.
- Il launcher `run.py` avvia entrambi i processi con un unico comando.

---

## 5. Frontend: Streamlit

### Cos'è Streamlit

**Streamlit** è un framework Python che permette di creare applicazioni web interattive scrivendo solo Python — nessun HTML, CSS o JavaScript necessario (anche se è possibile iniettarli tramite `st.markdown(..., unsafe_allow_html=True)`).

Il modello di esecuzione di Streamlit è **re-run on interaction**: ogni volta che l'utente interagisce con un widget (pulsante, slider, text area), l'intero script Python viene rieseguito dall'alto verso il basso. Lo stato persistente tra i rerun viene gestito con `st.session_state`.

### Come viene usato in PromptDoctor

Il file principale è [src/app.py](src/app.py).

#### Configurazione pagina

```python
st.set_page_config(
    page_title="PromptDoctor",
    page_icon="🤖",
    layout="wide"
)
```

`layout="wide"` espande il contenuto a tutta la larghezza del browser.

#### Session State

```python
if "high_score_count" not in st.session_state:
    st.session_state.high_score_count = 0

if "api_client" not in st.session_state:
    st.session_state.api_client = PromptAPIClient()
```

`st.session_state` è un dizionario persistente per l'intera sessione browser. Viene usato per:
- Tracciare il contatore di score alti (easter egg)
- Mantenere il singleton `PromptAPIClient`
- Memorizzare il `custom_context` caricato dall'utente (RAG)

#### Widget principali

```python
# Input problema
problem_desc = st.text_area("Descrivi il tuo problema", height=120)

# Toggle AI
use_ai = st.toggle("Attiva AI Engine (Ollama)", value=False)

# Analisi live (si attiva ad ogni keystroke)
if problem_desc:
    result = api_client.analyze_text(problem_desc, use_ai, custom_context)
    render_badges(result["matches"], result["used_ai"])

# Genera prompt
if st.button("GENERA PROMPT PERFETTO!"):
    with st.spinner("Generazione in corso..."):
        response = api_client.generate_prompt(payload)
```

#### Rendering risultati

```python
st.code(final_prompt, language="markdown")

# DataFrame CO-STAR
df = pd.DataFrame(costar_items)
st.dataframe(df, use_container_width=True)

# Easter egg
if score > 90:
    st.session_state.high_score_count += 1
    if st.session_state.high_score_count == 5:
        st.balloons()
        st.toast("Sei un prompt engineer!")
```

#### Iniezione CSS

Streamlit permette di iniettare CSS custom tramite `st.markdown`:

```python
st.markdown(f"<style>{CSS_THEME}</style>", unsafe_allow_html=True)
```

Il tema usa **Glassmorphism**: sfondi semi-trasparenti con `backdrop-filter: blur()`, gradienti, e animazioni CSS per i badge.

#### File uploader (RAG)

```python
uploaded_file = st.file_uploader("Carica contesto aziendale", type=["txt","md","csv"])
if uploaded_file:
    st.session_state.custom_context = uploaded_file.read().decode("utf-8")
```

Il contenuto del file viene passato al backend come `custom_context` per contestualizzare l'analisi AI.

---

## 6. Backend: FastAPI + Uvicorn

### Cos'è FastAPI

**FastAPI** è un framework Python moderno per API REST, basato sugli standard OpenAPI e JSON Schema. È asincrono (ASGI), usa type hints Python per la validazione automatica dei dati tramite **Pydantic**, e genera documentazione interattiva (`/docs`) automaticamente.

**Uvicorn** è il server ASGI che esegue l'applicazione FastAPI.

### Come viene usato in PromptDoctor

Il file principale è [src/api_server.py](src/api_server.py).

#### Creazione dell'app e CORS

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PromptDoctor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Il middleware CORS permette al frontend Streamlit (porta 8501) di fare richieste al backend (porta 8000) senza errori di cross-origin.

#### Singleton dei core modules

```python
# Istanziati UNA VOLTA all'avvio — mai ri-creati ad ogni request
pattern_engine = PatternEngine()
revisor = MultiAgentRevisor()
db_manager = PromptDBManager()
```

Questo è fondamentale per le performance: creare un'istanza LangGraph o connettersi a Ollama ad ogni richiesta sarebbe lento.

#### Modelli Pydantic (validazione input)

```python
class AnalyzeRequest(BaseModel):
    problem_desc: str
    use_ai: bool = False
    custom_context: str = ""

class GenerateRequest(BaseModel):
    problem_desc: str
    obiettivo: str
    ruolo: str
    framework: str
    lingua: str
    dettaglio: int
    is_iterativo: bool
    use_ai: bool = False
    custom_context: str = ""
```

Pydantic valida automaticamente i tipi: se il frontend invia `dettaglio` come stringa, FastAPI restituisce un errore 422 prima ancora di entrare nella funzione.

#### Endpoints

**POST /api/analyze_text** — analisi live (chiamata ad ogni keystroke)

```python
@app.post("/api/analyze_text")
async def analyze_text(request: AnalyzeRequest):
    matches, modifiers, used_ai = pattern_engine.analyze_text(
        request.problem_desc,
        request.use_ai,
        request.custom_context
    )
    return {"matches": matches, "modifiers": modifiers, "used_ai": used_ai}
```

**POST /api/generate_prompt** — endpoint principale

```python
@app.post("/api/generate_prompt")
async def generate_prompt(request: GenerateRequest):
    # 1. Pattern matching
    matches, modifiers, used_ai = pattern_engine.analyze_text(...)

    # 2. Build stack tecnologico
    stack = [request.framework] + list(modifiers.get("framework", set()))

    # 3. Multi-agent AI (opzionale)
    ai_result = None
    if request.use_ai:
        ai_result = revisor.rewrite_text(request.problem_desc)

    # 4. CO-STAR sempre generato (fallback)
    costar = generate_costar(request.obiettivo, request.ruolo, ...)

    # 5. Selezione prompt finale
    final_prompt = ai_result["final_prompt"] if ai_result else costar["final"]

    # 6. Score
    score_data = calculate_score(...)

    # 7. Persistenza
    db_manager.save_prompt(request.problem_desc, final_prompt, score_data["total"])

    return { "final_prompt": final_prompt, "score": score_data["total"], ... }
```

**GET /api/history** — storico

```python
@app.get("/api/history")
async def get_history():
    return db_manager.get_all_prompts()
```

#### Avvio

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
```

`reload=True` riavvia il server automaticamente ad ogni modifica del codice (utile in development).

---

## 7. AI Engine: Ollama + LangChain + LangGraph

### Ollama

**Ollama** è un runtime che permette di eseguire Large Language Models localmente. Espone un'API REST compatibile su `http://localhost:11434`.

In PromptDoctor, Ollama serve come backend LLM per due componenti:
1. `PatternEngine._ai_analysis()` — analisi semantica del testo con output JSON strutturato
2. `MultiAgentRevisor` — i 4 nodi del workflow multi-agent

Il modello usato è **llama3.2** (configurabile in `config.py`).

**Chiamata diretta (PatternEngine):**

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": prompt_text,
        "stream": False,
        "format": "json"   # forza output JSON valido
    }
)
result = json.loads(response.json()["response"])
```

L'opzione `"format": "json"` istruisce Ollama a restituire solo JSON valido, evitando testo libero difficile da parsare.

### LangChain

**LangChain** è un framework per costruire applicazioni basate su LLM. I concetti chiave usati in PromptDoctor:

#### PromptTemplate

```python
from langchain.prompts import PromptTemplate

judge_template = PromptTemplate(
    input_variables=["original_request"],
    template="""
    Sei un esperto critico di prompt AI.
    Valuta questa richiesta: {original_request}
    
    Rispondi in JSON: {{"score": 0-100, "analisi": "..."}}
    """
)
```

`PromptTemplate` separa il template dalla variabile — quando il nodo viene eseguito, `{original_request}` viene sostituito con il valore reale.

#### LLM via LangChain-Community

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3.2")
```

LangChain-Community fornisce l'integrazione con Ollama. `Ollama` è un wrapper che trasforma il modello in un oggetto compatibile con le catene LangChain.

#### Chain (LCEL - LangChain Expression Language)

```python
chain = judge_template | llm
result = chain.invoke({"original_request": testo})
```

L'operatore `|` (pipe) compone il template con l'LLM: prima formatta il prompt, poi lo manda all'LLM. Questa sintassi è la nuova **LCEL** (LangChain Expression Language).

#### StreamlitCallbackHandler

```python
from langchain.callbacks import StreamlitCallbackHandler

container = st.empty()
callbacks = [StreamlitCallbackHandler(container)]
chain.invoke({"original_request": testo}, config={"callbacks": callbacks})
```

Questo handler permette di visualizzare i token generati in tempo reale dentro un container Streamlit — il testo appare progressivamente come nella chat di ChatGPT.

### LangGraph

**LangGraph** è un'estensione di LangChain che permette di costruire workflow complessi con agenti multipli, usando un grafo orientato (DAG o con cicli).

I concetti chiave:

#### StateGraph e AgentState

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    original_request: str   # Input iniziale
    analysis: str           # Output dell'Analyst
    architecture: str       # Output dell'Architect
    final_prompt: str       # Output del Prompt Writer
    score_ai: int           # Output del Judge
    giudizio_critico: str   # Testo critico del Judge
```

`AgentState` è un dizionario tipizzato che rappresenta lo stato condiviso tra tutti i nodi. Ogni nodo riceve lo stato corrente, lo modifica, e lo passa al nodo successivo.

#### Nodi

```python
def _judge_node(self, state: AgentState) -> AgentState:
    chain = self.judge_template | self.llm
    result = chain.invoke({"original_request": state["original_request"]})
    
    # Estrazione robusta del JSON con regex (fallback se il JSON è malformato)
    json_match = re.search(r'\{.*?\}', result, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group())
        score = data.get("score", 50)
        analisi = data.get("analisi", "")
    
    return {**state, "score_ai": score, "giudizio_critico": analisi}
```

Ogni nodo è un metodo che:
1. Riceve `state: AgentState`
2. Chiama il suo LLM chain
3. Aggiorna lo stato con i suoi risultati
4. Ritorna il nuovo stato (con `{**state, "chiave": valore}` per non perdere i campi precedenti)

#### Costruzione del grafo

```python
graph_builder = StateGraph(AgentState)

graph_builder.add_node("judge", self._judge_node)
graph_builder.add_node("analyst", self._analyst_node)
graph_builder.add_node("architect", self._architect_node)
graph_builder.add_node("prompt_writer", self._prompt_writer_node)

graph_builder.set_entry_point("judge")
graph_builder.add_edge("judge", "analyst")
graph_builder.add_edge("analyst", "architect")
graph_builder.add_edge("architect", "prompt_writer")
graph_builder.add_edge("prompt_writer", END)

self.graph = graph_builder.compile()
```

Il grafo è **sequenziale**: Judge → Analyst → Architect → Prompt Writer. Non ci sono rami condizionali o cicli in questa implementazione.

#### Esecuzione

```python
initial_state = AgentState(
    original_request=testo,
    analysis="",
    architecture="",
    final_prompt="",
    score_ai=0,
    giudizio_critico=""
)
final_state = self.graph.invoke(initial_state)
```

`graph.invoke()` esegue tutti i nodi in sequenza e ritorna lo stato finale con tutti i campi popolati.

---

## 8. Pattern Engine (Doppio Motore)

Il file [src/core/pattern_engine.py](src/core/pattern_engine.py) implementa il riconoscimento di tecnologie nel testo tramite due meccanismi complementari.

### Analisi Statica (Regex)

```python
STATIC_TECH_PATTERNS = {
    r"(barcode|qr|code|scanner|lettur)": {
        "libs": "treepoem pillow pyzbar streamlit",
        "framework": "streamlit",
        "api": ""
    },
    r"(modifica|update|aggiorna|continua|riprendi)": {
        "iterative": True,
        "prefix": "**CONTINUA DAL PUNTO PRECEDENTE**\n\n"
    },
    r"(web app|dashboard|interfaccia|ui|streamlit)": {
        "libs": "streamlit pandas plotly",
        "framework": "streamlit"
    },
    r"(magic|mtg|deck|carta|mazzo)": {
        "libs": "pandas requests",
        "api": "scryfall",
        "framework": "streamlit"
    },
    # ... altri 4 pattern
}
```

Per ogni testo in input, il motore itera su tutti i pattern regex. Se c'è un match, accumula le librerie, i framework e le API rilevate in un dizionario `modifiers`.

```python
def _static_analysis(self, text: str):
    matches = []
    modifiers = {"libs": set(), "framework": set(), "api": set()}
    
    for pattern, config in STATIC_TECH_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pattern)
            if "libs" in config:
                modifiers["libs"].update(config["libs"].split())
            if "framework" in config:
                modifiers["framework"].add(config["framework"])
    
    return matches, modifiers, False
```

**Vantaggi**: veloce, deterministico, nessuna dipendenza da LLM.
**Limiti**: copre solo i pattern pre-definiti.

### Analisi AI (Ollama JSON)

```python
def _ai_analysis(self, text: str, custom_context: str = ""):
    rag_note = ""
    if custom_context:
        rag_note = f"""
        IMPORTANTE: usa ESCLUSIVAMENTE le tecnologie in questo documento aziendale:
        {custom_context}
        """
    
    prompt = f"""
    Sei un software architect. Analizza il seguente testo e identifica:
    - Tecnologie necessarie (libs, framework, API)
    - Pattern tecnici rilevanti
    
    {rag_note}
    
    Testo: {text}
    
    Rispondi SOLO in JSON:
    {{"matches": [...], "libs": [...], "framework": [...], "api": [...]}}
    """
    
    response = requests.post(OLLAMA_API_URL, json={
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    })
    
    return json.loads(response.json()["response"])
```

Il pattern **RAG (Retrieval-Augmented Generation)** funziona così: se l'utente carica un file aziendale (es. `tech_stack_aziendale.md`), il suo contenuto viene iniettato nel prompt come contesto prioritario. L'LLM viene istruito a usare SOLO quelle tecnologie.

### Logica di Selezione

```python
def analyze_text(self, text, use_ai=False, custom_context=""):
    if use_ai:
        try:
            matches, modifiers, _ = self._ai_analysis(text, custom_context)
            if matches:
                return matches, modifiers, True  # used_ai = True
        except Exception:
            pass  # Fallback silenzioso
    
    # Fallback su analisi statica
    matches, modifiers, _ = self._static_analysis(text)
    return matches, modifiers, False
```

Il flag `used_ai` ritornato viene mostrato nell'UI come badge cyan "AI" invece del verde "STATIC".

---

## 9. Multi-Agent Workflow

Il file [src/core/agent_workflow.py](src/core/agent_workflow.py) implementa la pipeline a 4 agenti.

### I 4 Agenti

#### 1. Judge Node — Valutazione qualità

**Ruolo**: critico imparziale che assegna uno score da 0 a 100 alla richiesta originale.

**Template prompt**:
```
Sei un esperto critico di prompt AI.
Valuta la qualità di questa richiesta utente considerando:
- Chiarezza e specificità
- Presenza di contesto tecnico
- Completezza delle informazioni

Richiesta: {original_request}

Rispondi SOLO in JSON: {"score": numero_0_100, "analisi": "max_15_parole"}
```

**Output su stato**:
- `score_ai`: intero 0-100
- `giudizio_critico`: stringa breve di analisi

Il giudizio viene mostrato nell'UI sotto il prompt generato come feedback critico.

#### 2. Analyst Node — Estrazione requisiti

**Ruolo**: Business Analyst tecnico che struttura i requisiti.

**Template prompt**:
```
Sei un Technical Business Analyst.
Analizza questa richiesta ed estrai:
- Requisiti funzionali (cosa deve fare il sistema)
- Attori coinvolti (chi lo usa)
- Scenari d'uso principali
- Vincoli tecnici implici

Richiesta: {original_request}
```

**Output su stato**:
- `analysis`: elenco markdown strutturato

Questo output viene passato come input all'Architect.

#### 3. Architect Node — Proposta architetturale

**Ruolo**: Software Architect che propone stack e architettura.

**Template prompt**:
```
Sei un Software Architect esperto.
Basandoti su questa analisi dei requisiti:
{analysis}

Proponi:
- Architettura high-level del sistema
- Stack tecnologico consigliato
- Pattern architetturali da applicare
- Integrazioni necessarie

Sii specifico e pratico.
```

**Output su stato**:
- `architecture`: scelte architetturali in markdown

#### 4. Prompt Writer Node — Generazione prompt finale

**Ruolo**: Senior Prompt Engineer che produce il prompt definitivo.

Questo è il nodo più importante e riceve come input l'intera catena di lavoro precedente.

**Template prompt**:
```
Sei un Senior Prompt Engineer esperto.
Hai a disposizione:

RICHIESTA ORIGINALE: {original_request}
ANALISI REQUISITI: {analysis}
ARCHITETTURA PROPOSTA: {architecture}

LINEE GUIDA GEMINI: {guidelines}

Scrivi un prompt ottimizzato (150-300 parole) che:
1. Assegni un ruolo specifico all'AI
2. Descriva chiaramente l'attività
3. Fornisca contesto tecnico rilevante
4. Specifichi il formato di output desiderato
5. Usi linguaggio naturale, diretto, senza convenevoli

IMPORTANTE: Scrivi SOLO il prompt, senza intestazioni o spiegazioni.
```

Le `guidelines` sono le `GEMINI_PROMPT_GUIDELINES` definite in `config.py` — le linee guida ufficiali per la scrittura di prompt di alta qualità.

**Output su stato**:
- `final_prompt`: il prompt AI polished pronto all'uso

### Fallback Pattern

```python
def rewrite_text(self, text: str) -> dict:
    try:
        initial_state = AgentState(original_request=text, ...)
        final_state = self.graph.invoke(initial_state)
        return final_state
    except Exception as e:
        # Se il workflow fallisce (Ollama offline, timeout, ecc.)
        # restituisce il testo originale invariato
        return {
            "final_prompt": text,
            "score_ai": 50,
            "giudizio_critico": "Analisi non disponibile"
        }
```

Il fallback garantisce che l'applicazione rimanga funzionante anche se Ollama è offline: in quel caso, viene usato il CO-STAR generato staticamente.

---

## 10. Generazione Prompt CO-STAR

Il file [src/prompt_generator.py](src/prompt_generator.py) implementa la generazione strutturata secondo il framework **CO-STAR**.

### Il Framework CO-STAR

CO-STAR è un framework per la scrittura di prompt strutturati, con 6 sezioni:

| Sezione | Significato | Esempio |
|---|---|---|
| **C**ontext | Contesto e ruolo del richiedente | "Sono un AR Developer che lavora con Unity" |
| **O**bjective | Obiettivo principale e richiesta specifica | "Voglio creare un barcode scanner" |
| **S**tyle | Stile di codice richiesto | "Usa type hints, moduli separati, docstrings" |
| **T**one | Tono della risposta | "Tecnico, diretto, senza convenevoli" |
| **A**udience | Destinatario del prompt | "Un AI assistant per sviluppatori esperti" |
| **R**esponse | Formato atteso dell'output | "Script Python completo con commenti" |

### Implementazione

```python
def generate_costar(obiettivo, ruolo, framework, lingua, dettaglio,
                    is_iterativo, problem_desc, modifiers, stack):

    # CONTEXT — ruolo + nota iterativa
    context = f"Sono un {ruolo}"
    if is_iterativo:
        context += "\nStai lavorando su codice esistente — CONTINUA dal punto precedente."

    # OBJECTIVE — obiettivo + richiesta specifica
    objective = f"Obiettivo principale: {obiettivo}\nRichiesta specifica: {problem_desc}"

    # STYLE — stack tecnologico + livello di dettaglio
    libs_str = ", ".join(modifiers.get("libs", []))
    apis_str = ", ".join(modifiers.get("api", []))
    
    style_base = f"Stack: {', '.join(stack)}"
    if libs_str:
        style_base += f"\nLibrerie obbligatorie: {libs_str}"
    if apis_str:
        style_base += f"\nAPI da integrare: {apis_str}"
    
    # Il livello di dettaglio modifica lo stile
    if dettaglio >= 80:
        style_detail = "Struttura modulare, type hints ovunque, docstrings per ogni funzione."
    elif dettaglio <= 40:
        style_detail = "Codice compatto e funzionante. Nessun commento prolisso."
    else:
        style_detail = "Codice pulito e commentato dove necessario."
    
    style = f"{style_base}\n{style_detail}"

    # TONE
    tone = "Tecnico, diretto e formale. Evita convenevoli e frasi introduttive."

    # AUDIENCE
    audience = "Un AI assistant che risponde a uno sviluppatore esperto."

    # RESPONSE — lingua + formato
    response_format = "Italiano" if lingua == "Italiano" else "English"
    if "pandas" in libs_str.lower():
        response_format += "\nIncludi tabelle dati dove applicabile."
    if dettaglio >= 70:
        response_format += "\nScript Python completo, non snippet parziali."

    # Assembly
    final = f"""# CONTEXT
{context}

# OBJECTIVE
{objective}

# STYLE
{style}

# TONE
{tone}

# AUDIENCE
{audience}

# RESPONSE
{response_format}"""

    return {
        "context": context,
        "objective": objective,
        "style": style,
        "tone": tone,
        "audience": audience,
        "response": response_format,
        "final": final
    }
```

Il CO-STAR viene **sempre** generato come fallback, anche quando il workflow AI è attivo. Viene mostrato come "CO-STAR Breakdown" nell'expander, permettendo all'utente di capire la struttura del prompt.

---

## 11. Sistema di Score e Gamification

Il file [src/utils/score.py](src/utils/score.py) implementa un sistema di scoring multi-dimensionale che valuta la qualità del prompt generato.

### Categorie di Punteggio

```python
def calculate_score(problem_desc, modifiers, stack, is_iterativo,
                    prompt_tokens, used_ai, ai_judge_score=None):

    # Categoria 1: Setup tecnologico (max 20pt)
    # Ha senso specificare librerie o framework?
    has_libs = bool(modifiers.get("libs")) or len(stack) > 1
    s_setup = 20 if has_libs else 0

    # Categoria 2: Richiesta tabelle (max 15pt)
    # I prompt con output tabellare sono più strutturati
    needs_table = "tabell" in problem_desc.lower() or "pandas" in str(modifiers.get("libs",""))
    s_table = 15 if needs_table else 0

    # Categoria 3: Approccio iterativo (max 20pt)
    # Few-shot / continuation context migliora la precisione
    s_fewshot = 20 if is_iterativo else 0

    # Categoria 4: Specificità richiesta (max 25pt)
    # Più la descrizione è dettagliata, meglio è
    word_count = len(problem_desc.split())
    s_specs = 25 if word_count > 8 else 10

    # Categoria 5: Lunghezza prompt ottimale (max 20pt)
    # Un prompt tra 40 e 250 token è nel range ottimale
    s_tokens = 20 if 40 <= prompt_tokens <= 250 else 15

    # Categoria 6: Bonus AI (max 10pt — extra, può superare 100)
    s_ai_bonus = 10 if (used_ai and modifiers) else 0

    # Score base
    base_score = min(100, s_setup + s_table + s_fewshot + s_specs + s_tokens + s_ai_bonus)

    # Weighted average con score del Judge AI
    if ai_judge_score is not None and used_ai:
        total = int(ai_judge_score * 0.6 + base_score * 0.4)
    else:
        total = base_score

    return {
        "total": total,
        "setup": s_setup,
        "table": s_table,
        "fewshot": s_fewshot,
        "specs": s_specs,
        "tokens": s_tokens,
        "ai_bonus": s_ai_bonus,
        "suggestions": _get_suggestions(s_setup, s_table, s_fewshot, s_specs)
    }
```

### Weighted Average AI

Quando l'AI è attiva, lo score finale è una **media pesata**:
- 60% score del Judge AI (valutazione semantica della richiesta)
- 40% score basato su regole (valutazione strutturale del prompt)

Questo equilibra la valutazione qualitativa dell'LLM con criteri oggettivi e deterministici.

### Suggestions System

```python
def _get_suggestions(s_setup, s_table, s_fewshot, s_specs):
    suggestions = []
    if s_table == 0:
        suggestions.append("Richiedi output in formato tabellare per maggiore struttura")
    if s_fewshot == 0:
        suggestions.append("Attiva l'approccio iterativo se stai continuando codice esistente")
    if s_setup == 0:
        suggestions.append("Specifica framework e librerie, o attiva l'AI Engine")
    if s_specs < 25:
        suggestions.append("Aggiungi più dettagli tecnici alla descrizione del problema")
    return suggestions
```

Le suggestions vengono mostrate nell'UI con icone Font Awesome, guidando l'utente a migliorare il prompt.

### Easter Egg

```python
# In app.py, dopo ogni generazione
if response["score"] > 90:
    st.session_state.high_score_count += 1
    if st.session_state.high_score_count >= 5:
        st.balloons()
        st.toast("Sei un vero Prompt Engineer!", icon="🏆")
        st.session_state.high_score_count = 0  # reset
```

Cinque score consecutivi sopra 90 attivano l'animazione dei palloncini di Streamlit.

---

## 12. Database: SQLite3 (DAO Pattern)

Il file [src/core/db_manager.py](src/core/db_manager.py) implementa il pattern **DAO (Data Access Object)** per la persistenza dei prompt.

### Schema del Database

```sql
CREATE TABLE IF NOT EXISTS prompts_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    original_input  TEXT    NOT NULL,
    generated_prompt TEXT   NOT NULL,
    score           INTEGER NOT NULL
);
```

SQLite3 è un database embedded: non richiede un processo server separato. Il file `prompts_history.db` viene creato automaticamente al primo avvio nella root del progetto.

### Implementazione DAO

```python
import sqlite3
from datetime import datetime
from pathlib import Path

class PromptDBManager:
    def __init__(self):
        db_path = Path(__file__).parents[2] / "prompts_history.db"
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompts_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    original_input TEXT NOT NULL,
                    generated_prompt TEXT NOT NULL,
                    score INTEGER NOT NULL
                )
            """)
            conn.commit()

    def save_prompt(self, original_input: str, generated_prompt: str, score: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO prompts_history (timestamp, original_input, generated_prompt, score) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), original_input, generated_prompt, score)
            )
            conn.commit()

    def get_all_prompts(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Righe come dizionari
            cursor = conn.execute(
                "SELECT * FROM prompts_history ORDER BY timestamp DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
```

Il context manager `with sqlite3.connect(...)` gestisce automaticamente apertura, commit e chiusura della connessione.

`conn.row_factory = sqlite3.Row` trasforma ogni riga del risultato in un oggetto accessibile sia per indice che per nome colonna — quando convertito con `dict()`, produce dizionari direttamente serializzabili in JSON da FastAPI.

---

## 13. Comunicazione HTTP: api_client.py

Il file [src/api_client.py](src/api_client.py) è un **Adapter** che incapsula tutte le chiamate HTTP dal frontend al backend.

```python
import requests

class PromptAPIClient:
    BASE_URL = "http://localhost:8000/api"

    def analyze_text(self, problem_desc: str, use_ai: bool, custom_context: str = "") -> dict:
        try:
            r = requests.post(f"{self.BASE_URL}/analyze_text", json={
                "problem_desc": problem_desc,
                "use_ai": use_ai,
                "custom_context": custom_context
            }, timeout=10)
            return r.json()
        except Exception:
            return {"matches": [], "modifiers": {}, "used_ai": False}

    def generate_prompt(self, payload: dict) -> dict | None:
        try:
            r = requests.post(f"{self.BASE_URL}/generate_prompt", json=payload, timeout=120)
            return r.json()
        except Exception:
            return None

    def get_history(self) -> list:
        try:
            r = requests.get(f"{self.BASE_URL}/history", timeout=5)
            return r.json()
        except Exception:
            return []
```

I timeout sono calibrati diversamente:
- `analyze_text`: 10 secondi (veloce, anche con AI statica)
- `generate_prompt`: 120 secondi (il workflow multi-agent può richiedere tempo)
- `get_history`: 5 secondi (semplice query DB)

In caso di errore, il client ritorna valori di default sicuri invece di propagare l'eccezione — questo garantisce che il frontend non si blocchi se il backend è temporaneamente offline.

---

## 14. UI Components e Stile

### components.py

Il file [src/ui/components.py](src/ui/components.py) separa i componenti UI riutilizzabili dall'app principale.

#### render_sidebar()

```python
def render_sidebar() -> tuple[str, str, str, str, int, bool, str]:
    with st.sidebar:
        st.title("Configurazione")

        obiettivo = st.text_input("Obiettivo del prompt")

        ruolo = st.selectbox("Ruolo", [
            "AR Developer", "Data Scientist", "Frontend Developer",
            "Backend Developer", "Fullstack Developer", "Hobbyist"
        ])

        framework = st.selectbox("Framework principale", [
            "Streamlit", "Flask", "React", "Unity", "Django", "Nessuno"
        ])

        lingua = st.selectbox("Lingua output", ["Italiano", "English"])

        dettaglio = st.slider("Livello di dettaglio", 25, 100, 75, step=5)

        is_iterativo = st.toggle("Modalità iterativa (modifica codice esistente)")

        # RAG: upload contesto aziendale
        uploaded = st.file_uploader("Carica contesto aziendale", type=["txt","md","csv"])
        custom_context = ""
        if uploaded:
            custom_context = uploaded.read().decode("utf-8")
            st.session_state.custom_context = custom_context

        return obiettivo, ruolo, framework, lingua, dettaglio, is_iterativo, custom_context
```

#### render_badges()

```python
def render_badges(matches: list, used_ai: bool):
    if not matches:
        return
    
    badge_class = "badge-ai" if used_ai else "badge"
    icon = "🧠" if used_ai else "🔍"
    
    html = " ".join([
        f'<span class="{badge_class}">{icon} {m.upper()}</span>'
        for m in matches
    ])
    st.markdown(html, unsafe_allow_html=True)
```

#### render_score_ui()

```python
def render_score_ui(score_data: dict):
    total = score_data["total"]
    color = "#10b981" if total >= 80 else "#f59e0b" if total >= 60 else "#ef4444"
    
    st.markdown(f"""
    <div class="score-card">
        <div class="score-total" style="color: {color}">{total}/100</div>
        <div class="score-breakdown">
            <span><i class="fas fa-cog"></i> Setup: {score_data['setup']}</span>
            <span><i class="fas fa-table"></i> Tabelle: {score_data['table']}</span>
            <span><i class="fas fa-redo"></i> Iterativo: {score_data['fewshot']}</span>
            <span><i class="fas fa-list"></i> Specifiche: {score_data['specs']}</span>
            <span><i class="fas fa-ruler"></i> Lunghezza: {score_data['tokens']}</span>
            {f'<span style="color: #a855f7"><i class="fas fa-brain"></i> AI Bonus: {score_data["ai_bonus"]}</span>' if score_data.get("ai_bonus") else ""}
        </div>
        {"".join([f'<p class="suggestion">⚠️ {s}</p>' for s in score_data.get("suggestions", [])])}
    </div>
    """, unsafe_allow_html=True)
```

### CSS Theme (config.py)

Il tema visivo è **Glassmorphism** con accenti verde (`#10b981`):

```css
/* Glassmorphism sidebar */
.css-1d391kg {
    background: rgba(17, 24, 39, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(16, 185, 129, 0.3) !important;
}

/* Badge animato */
.badge {
    background: linear-gradient(135deg, #10b981, #059669);
    padding: 4px 12px;
    border-radius: 20px;
    animation: pulse-glow 2s infinite;
}

/* Badge AI con cyan glow */
.badge-ai {
    background: linear-gradient(135deg, #06b6d4, #0891b2);
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
    animation: pulse-glow-cyan 2s infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.3); }
    50%       { box-shadow: 0 0 20px rgba(16, 185, 129, 0.8); }
}
```

Font Awesome viene caricato tramite CDN nel CSS iniettato con `st.markdown`.

---

## 15. Flusso Dati End-to-End

Di seguito il percorso completo di una richiesta tipica con AI attiva:

```
UTENTE
  │
  ├─ Digita: "Voglio creare un barcode scanner per la mia app"
  │  Configura: Ruolo=AR Dev, Framework=Streamlit, Dettaglio=75%, AI=ON
  │
  ▼ (Live analysis - ad ogni keystroke)
  
POST /api/analyze_text
  ├─ PatternEngine._ai_analysis()
  │  └─ Ollama prompt → "barcode, scanner, treepoem, pyzbar, pillow"
  └─ Response: {matches: ["barcode"], modifiers: {libs: ["treepoem","pyzbar"]}, used_ai: true}
  
  ▼ (Frontend)
  
Badge: "🧠 BARCODE" (cyan, animato)
  
  │ User clicca "GENERA PROMPT PERFETTO!"
  │
  ▼

POST /api/generate_prompt
  ├─ PatternEngine.analyze_text() → stesse matches/modifiers
  ├─ stack = ["Streamlit", "streamlit"]  (user + detected)
  │
  ├─ MultiAgentRevisor.rewrite_text("Voglio creare un barcode scanner...")
  │  │
  │  ├─ [Judge]
  │  │  └─ LLM → {"score": 68, "analisi": "Richiesta chiara ma manca contesto uso"}
  │  │  └─ state.score_ai = 68, state.giudizio_critico = "Richiesta chiara..."
  │  │
  │  ├─ [Analyst]
  │  │  └─ LLM → "- Scansione QR/Barcode da camera\n- Storage codici scansionati\n- UI mobile-friendly"
  │  │  └─ state.analysis = "..."
  │  │
  │  ├─ [Architect]
  │  │  └─ LLM → "Stack: Python + Streamlit\nLibrerie: pyzbar, pillow, OpenCV\nDB: SQLite"
  │  │  └─ state.architecture = "..."
  │  │
  │  └─ [Prompt Writer]
  │     └─ LLM → "Sei uno sviluppatore Python esperto. Crea un'applicazione Streamlit
  │                per la scansione di barcode/QR code con le seguenti caratteristiche:
  │                [... 200 parole polished ...]"
  │     └─ state.final_prompt = "..."
  │
  ├─ generate_costar()
  │  └─ CO-STAR structure con context/objective/style/tone/audience/response
  │
  ├─ final_prompt = state.final_prompt (AI vince sul CO-STAR)
  ├─ tokens = 187
  │
  ├─ calculate_score()
  │  ├─ s_setup = 20 (libs presenti)
  │  ├─ s_table = 0  (nessuna tabella richiesta)
  │  ├─ s_fewshot = 0 (non iterativo)
  │  ├─ s_specs = 25 (>8 parole)
  │  ├─ s_tokens = 20 (187 token, nel range)
  │  ├─ s_ai_bonus = 10 (AI attivo + modifiers)
  │  ├─ base = min(100, 75) = 75
  │  └─ weighted = (68 * 0.6) + (75 * 0.4) = 40.8 + 30 = 71
  │
  ├─ db_manager.save_prompt("Voglio creare...", "Sei uno sviluppatore...", 71)
  │  └─ INSERT INTO prompts_history VALUES (...)
  │
  └─ Response JSON: {final_prompt, score: 71, score_data, costar_data, giudizio_critico}

  ▼ (Frontend)

st.code(final_prompt)        → "Sei uno sviluppatore Python esperto..."
render_score_ui(score_data)  → Card: 71/100, breakdown per categoria
Expander CO-STAR: tabella a 6 righe
Giudizio critico: "Richiesta chiara ma manca contesto uso"

score (71) < 90 → no easter egg
suggestion: "Richiedi output in formato tabellare per maggiore struttura"
```

---

## 16. Pattern Architetturali Usati

### 1. Client-Server (Loose Coupling)

Frontend Streamlit e backend FastAPI sono processi separati che comunicano via HTTP. Questo permette di:
- Scalare indipendentemente
- Riavviare il frontend senza perdere il singleton backend
- Sviluppare e testare i due layer separatamente

### 2. Singleton

```python
# api_server.py — creati UNA VOLTA all'avvio
pattern_engine = PatternEngine()
revisor = MultiAgentRevisor()
db_manager = PromptDBManager()
```

Evita la reinizializzazione dell'LLM (costosa in termini di memoria e tempo) ad ogni richiesta HTTP.

### 3. DAO (Data Access Object)

`PromptDBManager` incapsula completamente l'accesso a SQLite. Il resto del codice non sa nulla di SQL — chiama solo `save_prompt()` e `get_all_prompts()`.

### 4. Adapter

`PromptAPIClient` è un adapter che traduce le chiamate Python del frontend in richieste HTTP al backend, gestendo errori e timeout in modo trasparente.

### 5. Template Method (PromptTemplate LangChain)

Ogni agente definisce il proprio template di prompt come attributo della classe. Il metodo `invoke()` è il "template method" che tutti i nodi eseguono nella stessa sequenza: format template → call LLM → parse output.

### 6. Chain of Responsibility (Multi-Agent Pipeline)

Il workflow LangGraph implementa una catena di responsabilità: ogni agente ha uno scopo specifico e passa il risultato al successivo. Nessun agente sa cosa fa il precedente o il successivo.

### 7. Strategy (Dual Pattern Engine)

Il `PatternEngine` può usare due strategie intercambiabili: analisi regex (statica, veloce) o analisi LLM (semantica, lenta). La strategia viene selezionata a runtime in base al flag `use_ai`.

### 8. RAG (Retrieval-Augmented Generation)

Il file aziendale caricato dall'utente viene "retrieved" (letto) e "augmented" nel prompt inviato all'LLM, permettendo risposte contestualizzate al tech stack specifico dell'azienda.

---

## 17. Test Suite

### test_pattern_engine.py

```python
def test_static_pattern_detection():
    engine = PatternEngine()
    matches, modifiers, used_ai = engine.analyze_text(
        "Voglio un barcode scanner per la mia app",
        use_ai=False
    )
    assert "barcode" in " ".join(matches).lower()
    assert "treepoem" in modifiers["libs"]
    assert "streamlit" in modifiers["framework"]
    assert used_ai == False

def test_iterator_pattern():
    engine = PatternEngine()
    matches, modifiers, _ = engine.analyze_text("Modifica il codice esistente", use_ai=False)
    assert modifiers.get("iterative") == True
    assert "CONTINUA" in modifiers.get("prefix", "")

def test_no_pattern():
    engine = PatternEngine()
    matches, modifiers, _ = engine.analyze_text("Voglio qualcosa di bello", use_ai=False)
    assert len(matches) == 0
```

### test_agent_workflow.py

```python
from unittest.mock import patch, MagicMock

def test_multi_agent_workflow_success():
    with patch("agent_workflow.Ollama") as mock_ollama:
        mock_llm = MagicMock()
        mock_ollama.return_value = mock_llm
        
        revisor = MultiAgentRevisor()
        
        with patch.object(revisor, "graph") as mock_graph:
            mock_graph.invoke.return_value = {
                "final_prompt": "Prompt generato",
                "score_ai": 80,
                "giudizio_critico": "Ottima richiesta"
            }
            result = revisor.rewrite_text("Test input")
            assert result["final_prompt"] == "Prompt generato"
            mock_graph.invoke.assert_called_once()

def test_multi_agent_fallback_on_error():
    revisor = MultiAgentRevisor()
    with patch.object(revisor, "graph") as mock_graph:
        mock_graph.invoke.side_effect = Exception("Ollama offline")
        result = revisor.rewrite_text("Test input")
        assert result["final_prompt"] == "Test input"  # Fallback = input originale
```

### test_prompt_writer.py (Integration)

Script di integration test manuale che avvia richieste reali al server FastAPI:

```
TEST 1 — Prompt Writer AI
  POST /api/generate_prompt {use_ai: true, problem_desc: "..."}
  Assert: score_ai presente, giudizio_critico non vuoto, used_ai_prompt == true

TEST 2 — CO-STAR Fallback
  POST /api/generate_prompt {use_ai: false, problem_desc: "..."}
  Assert: used_ai_prompt == false, final_prompt contiene "# CONTEXT"
```

---

## 18. Dipendenze e Versioni

### requirements.txt (dichiarate)

```
streamlit>=1.30.0
pandas>=2.0.0
requests>=2.31.0
ollama>=0.1.6
transformers>=4.37.0
torch>=2.1.0
pytest>=8.0.0
```

### Dipendenze aggiuntive (installate nel virtualenv)

```
fastapi
uvicorn[standard]
pydantic>=2.0
langchain
langchain-community
langgraph
```

### Runtime esterno richiesto

- **Ollama** — installato e avviato separatamente ([ollama.ai](https://ollama.ai))
  - Modello scaricato: `ollama pull llama3.2`
  - Server in ascolto su `http://localhost:11434`

---

## 19. Come Avviare il Progetto

### Setup iniziale

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

Crea il virtualenv e installa le dipendenze.

### Avvio

```bash
python run.py
```

`run.py` avvia in parallelo:
1. **FastAPI backend** su `http://localhost:8000` (via `uvicorn`)
2. **Streamlit frontend** su `http://localhost:8501` (via `streamlit run`)

L'applicazione si apre automaticamente nel browser su `http://localhost:8501`.

### Prerequisito Ollama (per AI Engine)

```bash
# Installa Ollama da https://ollama.ai
ollama pull llama3.2   # ~2GB download
ollama serve           # Avvia il server (o è già avviato come servizio)
```

Senza Ollama, l'applicazione funziona ugualmente usando solo l'analisi statica regex e il generatore CO-STAR.

---

*Documento generato analizzando il codice sorgente del progetto PromptDoctor.*
