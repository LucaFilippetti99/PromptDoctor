import streamlit as st
from typing import Tuple, List

def render_sidebar() -> Tuple[str, str, str, str, int, bool]:
    """Renders the settings sidebar and returns user inputs."""
    with st.sidebar:
        st.markdown("### <i class='fa-solid fa-bullseye' style='color:#10b981;'></i> Obiettivo e Profilo", unsafe_allow_html=True)
        
        obiettivo = st.text_input("🍏 Obiettivo", placeholder="Es. Creare un tool interno per i dati", value="Costruire una web app da zero")
        ruolo = st.selectbox("👥 Ruolo", ["AR Dev", "Data Scientist", "Frontend Engineer", "Backend Dev", "Fullstack", "Hobbyist"], index=0)
        framework = st.selectbox("⚙️ Framework", ["Streamlit", "Flask", "React", "Unity", "Django", "Nessuno in particolare"], index=0)
        lingua = st.selectbox("🌍 Lingua output", ["Italiano", "English"])
        dettaglio = st.slider("📏 Livello di dettaglio", min_value=25, max_value=100, value=75, step=5, format="%d%%")
        is_iterativo = st.toggle("🔄 Modifica codice esistente (Iterativo)", value=False)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #94a3b8; font-size: 0.85em; margin-top: 20px;'>
            <i class="fa-solid fa-rocket" style="color:#10b981;"></i> PromptDoctor v2.0 <span class="gradient-text">PRO</span><br>
            <span style="font-size: 0.8em;">Local LLM Ready</span>
        </div>
        """, unsafe_allow_html=True)
        
    return obiettivo, ruolo, framework, lingua, dettaglio, is_iterativo

def render_badges(matches: List[str], used_ai: bool):
    """Renders badges for detected tech patterns."""
    if not matches:
        return
        
    badge_class = "badge-ai" if used_ai else "badge"
    icon = '<i class="fa-solid fa-brain"></i>' if used_ai else '<i class="fa-solid fa-magnifying-glass"></i>'
    badges_html = "".join([f'<span class="{badge_class}">{icon} {m.upper()}</span>' for m in matches])
    st.markdown(f"<div style='margin-top: 10px; margin-bottom: 5px;'><span style='color: #94a3b8; font-size: 0.85em; font-weight: 600; letter-spacing: 0.5px;'>PATTERN RILEVATI:</span><br><br>{badges_html}</div>", unsafe_allow_html=True)

def render_score_ui(score_data: dict):
    """Renders the gamified score breakdown."""
    st.markdown(f"### <i class='fa-solid fa-star' style='color:#fbbf24;'></i> Score: {score_data['total']}/100", unsafe_allow_html=True)
    
    html_score = f"""
    <div class='glass-box' style='padding: 15px; margin-top: 10px;'>
        <ul style='list-style-type: none; padding-left: 0; margin-bottom: 0;'>
            <li style='margin-bottom: 5px;'><i class='fa-solid fa-check-circle' style='color:#10b981; margin-right:8px; width: 20px;'></i> <b>Setup eseguibile:</b> {score_data['setup']}/20</li>
            <li style='margin-bottom: 5px;'><i class='fa-solid fa-table' style='color:#10b981; margin-right:8px; width: 20px;'></i> <b>Tabelle usate:</b> {score_data['table']}/15</li>
            <li style='margin-bottom: 5px;'><i class='fa-solid fa-bolt' style='color:#10b981; margin-right:8px; width: 20px;'></i> <b>Few-shot:</b> {score_data['fewshot']}/20</li>
            <li style='margin-bottom: 5px;'><i class='fa-solid fa-microchip' style='color:#10b981; margin-right:8px; width: 20px;'></i> <b>Specifiche:</b> {score_data['specs']}/25</li>
            <li style='margin-bottom: 5px;'><i class='fa-solid fa-compress' style='color:#10b981; margin-right:8px; width: 20px;'></i> <b>Token ottimali:</b> {score_data['tokens']}/20</li>
    """
    if score_data.get('ai_bonus', 0) > 0:
        html_score += f"<li style='margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px;'><i class='fa-solid fa-brain' style='color:#c084fc; margin-right:8px; width: 20px;'></i> <b style='color:#c084fc;'>AI Bonus:</b> +{score_data['ai_bonus']}</li>"
        
    html_score += "</ul></div>"
    st.markdown(html_score, unsafe_allow_html=True)
    
    if score_data['total'] < 100 and score_data['suggestions']:
        suggestions_str = ', '.join(score_data['suggestions'])
        st.warning(f"💡 **Tip per migliorare:** Prova a: {suggestions_str}", icon="🚀")
