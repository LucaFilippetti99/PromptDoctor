# PromptDoctor.ai PRO 🩺✨

*A Vibe Coding Project - Built with AI* 🤖💻

PromptDoctor.ai PRO è uno strumento avanzato, gamificato e interattivo per il **Prompt Engineering**. Ti aiuta a generare prompt perfetti seguendo la struttura CO-STAR (Context, Objective, Style, Tone, Audience, Response), potenziando il processo con un'analisi semantica guidata da un **LLM Locale** (Ollama) orchestrato tramite LangGraph.

## 🧠 Cos'è il "Vibe Coding"?

Questo intero progetto è frutto del **Vibe Coding** (AI-Assisted Software Engineering). L'architettura del codice, la logica complessa dei nodi AI, l'interfaccia utente e persino lo streaming in tempo reale dei ragionamenti degli agenti sono stati realizzati interagendo, iterando e programmando a quattro mani con l'Intelligenza Artificiale.

## 🚀 Funzionalità Principali

- **Generatore CO-STAR**: Trasforma richieste generiche in prompt strutturati e altamente efficaci.
- **Multi-Agent Reasoning (LangGraph)**: Un vero e proprio team di agenti (Business Analyst e Software Architect) analizza le tue richieste in background.
- **Real-Time Streaming**: Effetto *Typewriter* in pieno stile ChatGPT che mostra in tempo reale nella UI i pensieri e il ragionamento generato dagli Agenti AI.
- **Local AI Pattern Engine**: Riconoscimento intelligente di framework e stack tecnologici grazie a LLM eseguiti localmente (sicuri e privati).
- **Gamification & Scoring**: Ogni prompt ottiene un punteggio basato su iterazioni, token e l'uso dell'AI. Punta alla streak perfetta di punteggi alti per sbloccare easter egg!
- **Prompt Library (Database)**: Salvataggio automatico di tutti i prompt generati in un DB SQLite locale per recuperarli comodamente in seguito.

## 🛠️ Stack Tecnologico

- **UI & Frontend**: [Streamlit](https://streamlit.io/) + Custom CSS
- **AI Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://www.langchain.com/langgraph)
- **Local LLM Integration**: [Ollama](https://ollama.com/)
- **Database**: SQLite3 (Integrato)

## 📦 Installazione e Avvio

1. Clona il repository.
2. Crea il tuo Virtual Environment e installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

3. Avvia [Ollama](https://ollama.com/) (assicurati che sia in esecuzione in background e di avere un modello scaricato, ad es. `ollama run mistral` o `llama3`).
4. Lancia l'app Streamlit:

   ```bash
   streamlit run app.py
   ```

Enjoy vibe coding! 🌊
