import streamlit as st
import time
import pandas as pd
import sys
import os

# Aggiungi la root del progetto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import CSS_THEME
from src.core.pattern_engine import PatternEngine
from src.core.agent_workflow import MultiAgentRevisor
from src.core.db_manager import PromptDBManager
from src.prompt_generator import generate_costar
from src.utils.score import calculate_score
from src.ui.components import render_sidebar, render_badges, render_score_ui

# ----------------- PAGE SETUP -----------------
st.set_page_config(
    page_title="PromptDoctor.ai PRO",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'high_score_count' not in st.session_state:
    st.session_state.high_score_count = 0
if 'engine' not in st.session_state:
    st.session_state.engine = PatternEngine()
if 'revisor' not in st.session_state:
    st.session_state.revisor = MultiAgentRevisor()
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = PromptDBManager()

# ----------------- UI STYLING -----------------
st.markdown(CSS_THEME, unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
obiettivo, ruolo, framework, lingua, dettaglio, is_iterativo = render_sidebar()

# ----------------- MAIN APP -----------------
st.markdown('<h1><i class="fa-solid fa-briefcase-medical" style="color: #10b981;"></i> PromptDoctor.ai <span class="gradient-text">PRO</span></h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.15rem; color: #a1a1aa; margin-top: -10px; margin-bottom: 20px;'>Il tuo Prompt Engineer personale potenziato con AI Pattern Recognition (Local LLM).</p>", unsafe_allow_html=True)

st.markdown('<div class="glass-box">', unsafe_allow_html=True)

# Problem Description Area
problem_desc = st.text_area(
    "✍️ Descrizione del problema o della richiesta", 
    height=140, 
    placeholder='Es: "Crea app per Magic: The Gathering deck analyzer..."'
)

# AI Hook
col_ai, col_empty = st.columns([1, 2])
with col_ai:
    use_ai = st.toggle("🧠 Usa AI Engine Locale (Ollama)", value=False)
if use_ai:
    st.info("💡 Attivo: l'LLM locale analizzerà in modo semantico il prompt per suggerire pattern di design e tecnologie!")

# Live Pattern Matching
matches = []
modifiers = {}
used_ai = False

if problem_desc:
    # Use the persistent PatternEngine instance
    matches, modifiers, used_ai = st.session_state.engine.analyze_text(problem_desc, use_ai=use_ai)
    
    if matches:
        render_badges(matches, used_ai)
        if modifiers.get('iterative'):
            is_iterativo = True
    else:
        st.caption("Nessun pattern tecnico noto rilevato nella richiesta.")

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- GENERATION LOGIC -----------------
st.markdown("<br>", unsafe_allow_html=True)
col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
with col_gen2:
    generate_btn = st.button("✨ GENERA PROMPT PERFETTO!", use_container_width=True)

if generate_btn:
    if not problem_desc:
        st.warning("⚠️ Inserisci una descrizione del problema prima di generare il prompt!")
    else:
        # Fun Progress Bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            time.sleep(0.005)
            progress_bar.progress(i + 1)
            if i == 20: status_text.text("⚙️ Estrazione pattern tecnici...")
            if i == 50: status_text.text("🏗️ Costruzione struttura CO-STAR...")
            if i == 80: status_text.text("📊 Calcolo score finale e rating...")
            
        status_text.empty()
        progress_bar.empty()
        
        # Determine stack logic to pass dynamically
        stack = []
        if framework != "Nessuno in particolare":
            stack.append(framework)
        if modifiers and modifiers.get('framework') and framework.lower() not in [f.lower() for f in modifiers['framework']]:
            stack.extend(list(modifiers['framework']))
            
        # AI Rewrite Step
        final_problem_desc = problem_desc
        if use_ai:
            status_text.text("🧠 Il Team di Agenti AI (Analyst, Architect) sta elaborando la tua richiesta...")
            
            # Crea UI divisa in Tabs per i vari agenti
            st.markdown("### 🧠 AI Reasoning in progress")
            tab_analyst, tab_architect = st.tabs(["🕵️‍♂️ Ragionamento Analyst", "🏗️ Proposta Architect"])
            
            with tab_analyst:
                st.caption("L'analista sta estrapolando i requisiti funzionali...")
                analyst_container = st.empty()
                
            with tab_architect:
                st.caption("L'architetto sta definendo lo stack e le scelte...")
                architect_container = st.empty()
            
            containers = {
                "analyst": analyst_container,
                "architect": architect_container
            }
            
            final_problem_desc = st.session_state.revisor.rewrite_text(problem_desc, containers=containers)
            
        # Generation
        prompt_data = generate_costar(
            obiettivo, ruolo, framework, lingua, dettaglio, 
            is_iterativo, final_problem_desc, modifiers, stack
        )
        final_prompt = prompt_data['final']
        
        # Scoring
        tokens = len(final_prompt.split())
        score_data = calculate_score(problem_desc, modifiers, stack, is_iterativo, tokens, used_ai)
        score = score_data['total']
        
        # Salvataggio nel DB (nascosto all'utente)
        st.session_state.db_manager.save_prompt(
            original_input=problem_desc, 
            generated_prompt=final_prompt, 
            score=score
        )
        
        if score > 90:
            st.session_state.high_score_count += 1
            if st.session_state.high_score_count >= 5:
                st.balloons()
                st.success("🏆 Prompt Master! Hai superato lo score di >90 per 5 volte di fila!")
                st.session_state.high_score_count = 0  # Reset for fun
        else:
            # reset streak on low score
            st.session_state.high_score_count = 0
        
        # ----------------- OUTPUT UI -----------------
        st.markdown("---")
        
        st.toast("Prompt generato e ottimizzato con successo! 🚀", icon="✅")
        
        col_res1, col_res2 = st.columns([1.6, 1])
        
        with col_res1:
            if use_ai and final_problem_desc != problem_desc:
                with st.expander("🤖 Richiesta Originale Ristrutturata dall'AI", expanded=False):
                    st.markdown(final_problem_desc)
            
            st.markdown("### <i class='fa-solid fa-wand-magic-sparkles' style='color:#10b981;'></i> Prompt Generato (Copia questo!)", unsafe_allow_html=True)
            st.code(final_prompt, language="markdown")
            
        with col_res2:
            render_score_ui(score_data)
                
        # CO-STAR Breakdown Table
        st.markdown("### <i class='fa-solid fa-list-check' style='color:#10b981;'></i> CO-STAR Preview", unsafe_allow_html=True)
        costar_df = [
            {"Sezione": "Context", "Contenuto": prompt_data['context']},
            {"Sezione": "Objective", "Contenuto": prompt_data['objective']},
            {"Sezione": "Style", "Contenuto": prompt_data['style']},
            {"Sezione": "Tone", "Contenuto": prompt_data['tone']},
            {"Sezione": "Audience", "Contenuto": prompt_data['audience']},
            {"Sezione": "Response", "Contenuto": prompt_data['response']}
        ]
        st.dataframe(pd.DataFrame(costar_df), use_container_width=True, hide_index=True)

# ----------------- STORICO PROMPT SALVATI -----------------
st.markdown("---")
st.markdown('### 💾 I Miei Prompt Salvati', unsafe_allow_html=True)

# Recupera e mostra i prompt dal database (caricati al re-run della pagina)
history = st.session_state.db_manager.get_all_prompts()

if not history:
    st.info("Non hai ancora salvato alcun prompt. Generane uno per vederlo qui sotto!")
else:
    for record in history:
        # Crea una preview breve da mostrare sul titolo dell'expander
        desc_preview = record['original_input']
        if len(desc_preview) > 60:
            desc_preview = desc_preview[:60] + "..."
            
        # Formatta la data dal formato ISO a uno più leggibile
        formatted_date = record['timestamp'][:16].replace('T', ' ')
        
        # Mostra l'expander iterativo
        with st.expander(f"🗓️ {formatted_date} | 🏆 Score: {record['score']} | 💬 {desc_preview}"):
            st.markdown("**👉 Richiesta Originale:**")
            st.info(record['original_input'])
            
            st.markdown("**✨ Prompt Generato (CO-STAR):**")
            # Usiamo st.code per abilitare il pulsante copia-incolla sulla destra di default in Streamlit
            st.code(record['generated_prompt'], language="markdown")
