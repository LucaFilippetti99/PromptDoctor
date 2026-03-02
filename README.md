# PromptDoctor 🩺✨

*A Vibe Coding Project - Built with AI* 🤖💻

PromptDoctor is an advanced, gamified, and interactive **Prompt Engineering** tool. It helps you generate perfect prompts following the CO-STAR structure (Context, Objective, Style, Tone, Audience, Response), enhancing the process with semantic analysis driven by a **Local LLM** (Ollama) orchestrated through LangGraph.

## 🧠 What is "Vibe Coding"?

This entire project is the result of **Vibe Coding** (AI-Assisted Software Engineering). The code architecture, the complex logic of the AI nodes, the user interface, and even the real-time Streamlit streaming of the agents' reasoning were created by interacting, iterating, and pairing with Artificial Intelligence.

## 🚀 Key Features

- **Client-Server Architecture**: Separated FastAPI backend for heavy AI logic and Streamlit frontend.
- **CO-STAR Generator**: Transforms generic requests into highly effective, structured prompts.
- **Multi-Agent Reasoning (LangGraph)**: A real team of agents (Business Analyst, Judge, and Software Architect) analyzes your requests in the background.
- **Local AI Pattern Engine**: Intelligent recognition of frameworks and tech stacks using locally executed LLMs (secure and private).
- **Gamification & Scoring**: Each prompt gets a score based on iterations, tokens, and AI usage. Aim for the perfect high-score streak to unlock Easter eggs!
- **Prompt Library (Database)**: Automatic saving of all generated prompts in a local SQLite DB to retrieve them easily later.

## 🛠️ Tech Stack

- **UI & Frontend (Client)**: [Streamlit](https://streamlit.io/) + Custom CSS
- **API Backend (Server)**: [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- **AI Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://www.langchain.com/langgraph)
- **Local LLM Integration**: [Ollama](https://ollama.com/)
- **Database**: SQLite3 (Embedded)

## 📦 Installation & Setup

1. Clone the repository.
2. Create your Virtual Environment and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start [Ollama](https://ollama.com/) (make sure it's running in the background and you have downloaded a model, e.g., `ollama run mistral` or `llama3`).

4. **Start the Application**:
   Open a terminal, activate your environment, and launch the main entry point which will automatically start both the backend server and the frontend UI:

   ```bash
   python run.py
   ```

   **Alternatively**, you can start the services manually in separate terminals:

   *API Backend Server*:

   ```bash
   uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload
   ```

   *Streamlit Frontend*:
   Open a *second* terminal and run:

   ```bash
   streamlit run src/app.py
   ```

Enjoy vibe coding! 🌊
