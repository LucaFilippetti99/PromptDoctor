import streamlit as st
import time
import pandas as pd
import sys
import os

# Aggiungi la root del progetto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import CSS_THEME
from src.api_client import PromptAPIClient
from src.ui.components import render_sidebar, render_badges, render_score_ui

# ----------------- PAGE SETUP -----------------
st.set_page_config(
    page_title="PromptDoctor.ai PRO",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'high_score_count' not in st.session_state:
    st.session_state.high_score_count = 0
if 'api_client' not in st.session_state:
    st.session_state.api_client = PromptAPIClient()

# ----------------- UI STYLING -----------------
st.html(CSS_THEME)

# ----------------- SIDEBAR -----------------
obiettivo, ruolo, framework, lingua, dettaglio, is_iterativo = render_sidebar()

# ----------------- MAIN APP -----------------
st.markdown('<h1><i class="fa-solid fa-briefcase-medical" style="color: #10b981;"></i> PromptDoctor.ai <span class="gradient-text">PRO</span></h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.15rem; color: #a1a1aa; margin-top: -10px; margin-bottom: 20px;'>Il tuo Prompt Engineer personale potenziato con AI Pattern Recognition.</p>", unsafe_allow_html=True)

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
    use_ai = st.toggle("🧠 Usa AI Engine Locale (Ollama via API)", value=False)
if use_ai:
    st.info("💡 Attivo: l'LLM locale nel Backend analizzerà in modo semantico il prompt per suggerire pattern di design e tecnologie!")

# Live Pattern Matching
matches = []
modifiers = {}
used_ai = False

if problem_desc:
    _custom_context = st.session_state.get('custom_context', '')
    matches, modifiers, used_ai = st.session_state.api_client.analyze_text(problem_desc, use_ai, _custom_context)
    
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
        payload = {
            "problem_desc": problem_desc,
            "use_ai": use_ai,
            "obiettivo": obiettivo,
            "ruolo": ruolo,
            "framework": framework,
            "lingua": lingua,
            "dettaglio": dettaglio,
            "is_iterativo": is_iterativo,
            "custom_context": st.session_state.get('custom_context', '')
        }
        
        with st.spinner("🤖 Generazione remota in corso... Il Backend sta elaborando la richiesta..."):
            try:
                # Chiamata API Rest
                response = st.session_state.api_client.generate_prompt(payload)
                
                final_prompt = response['final_prompt']
                score = response['score']
                score_data = response['score_data']
                giudizio_critico = response['giudizio_critico']
                final_problem_desc = response['final_problem_desc']
                prompt_data = response['costar_data']
                use_ai_backend = use_ai
                
                if score > 90:
                    st.session_state.high_score_count += 1
                    if st.session_state.high_score_count >= 5:
                        st.balloons()
                        st.success("🏆 Prompt Master! Hai superato lo score di >90 per 5 volte di fila!")
                        st.session_state.high_score_count = 0
                else:
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
                    if use_ai and giudizio_critico:
                        st.warning(f"🗣️ **Il Giudice AI dice:** {giudizio_critico}")
                        
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

            except Exception as e:
                st.error(f"❌ Errore Backend API: {e}")

# ----------------- STORICO PROMPT SALVATI -----------------
st.markdown("---")
st.markdown('### 💾 I Miei Prompt Salvati', unsafe_allow_html=True)

history = st.session_state.api_client.get_history()

if not history:
    st.info("Non hai ancora salvato alcun prompt. Generane uno per vederlo qui sotto (o Backend non online)!")
else:
    for record in history:
        desc_preview = record['original_input']
        if len(desc_preview) > 60:
            desc_preview = desc_preview[:60] + "..."
            
        formatted_date = record['timestamp'][:16].replace('T', ' ')
        
        with st.expander(f"🗓️ {formatted_date} | 🏆 Score: {record['score']} | 💬 {desc_preview}"):
            st.markdown("**👉 Richiesta Originale:**")
            st.info(record['original_input'])
            
            st.markdown("**✨ Prompt Generato (CO-STAR):**")
            st.code(record['generated_prompt'], language="markdown")
