import streamlit as st
import re
import time
import pandas as pd

# ----------------- PAGE SETUP -----------------
st.set_page_config(
    page_title="PromptDoctor.ai",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- UI STYLING -----------------
st.markdown("""
<style>
/* Base theme matching "carino" and "glassmorphism" */
.stApp {
    background-color: #0e1117;
    color: #f1f2f6;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.stButton>button {
    background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    width: 100%;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(255, 65, 108, 0.3);
    color: white;
}

.glass-box {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}

.badge {
    display: inline-block;
    padding: 0.35em 0.65em;
    font-size: 0.85em;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.375rem;
    background-color: rgba(40, 167, 69, 0.2);
    color: #4ade80;
    border: 1px solid #4ade80;
    margin-right: 8px;
    margin-bottom: 8px;
}

h1, h2, h3 {
    background: -webkit-linear-gradient(45deg, #FF416C, #FF4B2B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# ----------------- KNOWLEDGE BASE -----------------
TECH_PATTERNS = {
    r"(barcode|qr|code)": {"libs": "treepoem pillow qrcode faker", "pip": "pip install treepoem faker", "framework": "streamlit"},
    r"(web app|streamlit|ui)": {"framework": "streamlit", "ui": "st.sidebar st.image st.button"},
    r"(modifica|update|fix|change)": {"iterative": True, "prefix": "**CONTINUA DAL CODICE PRECEDENTE**\n**MODIFICA:**"},
    r"(ar|vr|unity|mrtk|xreal)": {"libs": "unity mrtk3 xreal-beam", "platform": "android xr"},
    r"(magic|mtg|deck|cards)": {"api": "scryfall", "libs": "pandas requests"},
    r"(cooking|recipe|nutrition)": {"api": "spoonacular", "libs": "pandas nutritionix"},
    r"(fitness|gym|training)": {"libs": "pandas matplotlib", "data": "strava api"}
}

def recognize_patterns(text):
    matched_patterns = []
    modifiers = {
        'libs': set(),
        'framework': set(),
        'prefix': '',
        'api': set(),
        'ui': set(),
        'platform': set(),
        'data': set(),
        'iterative': False
    }
    
    for pattern, data in TECH_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            matched_patterns.append(pattern)
            for k, v in data.items():
                if k == 'libs':
                    modifiers['libs'].update(v.split())
                elif k == 'framework':
                    modifiers['framework'].add(v)
                elif k == 'prefix':
                    modifiers['prefix'] = v
                elif k == 'api':
                    modifiers['api'].add(v)
                elif k == 'ui':
                    modifiers['ui'].update(v.split())
                elif k == 'platform':
                    modifiers['platform'].update(v.split())
                elif k == 'data':
                    modifiers['data'].update(v.split())
                elif k == 'iterative':
                    modifiers['iterative'] = True
                    
    return matched_patterns, modifiers

# ----------------- SESSION STATE -----------------
if 'high_score_count' not in st.session_state:
    st.session_state.high_score_count = 0

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### 🎯 Obiettivo e Profilo")
    
    obiettivo = st.text_input("🎯 Obiettivo", placeholder="Es. Creare un tool interno per i dati", value="Costruire una web app da zero")
    ruolo = st.selectbox("👥 Ruolo", ["AR Dev", "Data Scientist", "Frontend Engineer", "Backend Dev", "Fullstack", "Hobbyist"], index=0)
    framework = st.selectbox("⚙️ Framework", ["Streamlit", "Flask", "React", "Unity", "Django", "Nessuno in particolare"], index=0)
    lingua = st.selectbox("🌍 Lingua output", ["Italiano", "English"])
    dettaglio = st.slider("📏 Livello di dettaglio", min_value=25, max_value=100, value=75, step=5, format="%d%%")
    is_iterativo = st.toggle("🔄 Modifica codice esistente (Iterativo)", value=False)
    
    st.markdown("---")
    st.caption("🚀 PromptDoctor v1.0 - Gemini 3.1 Ready")

# ----------------- MAIN APP -----------------
st.markdown("<h1>🎯 PromptDoctor.ai</h1>", unsafe_allow_html=True)
st.markdown("### Il tuo Prompt Engineer personale (CO-STAR Framework)")

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
    use_ai = st.checkbox("🚀 AI Pattern Recognition (Fase 2)")
if use_ai:
    st.info("💡 Fase 2: Pronto per l'integrazione Ollama/Langchain!")

# Live Pattern Matching
if problem_desc:
    matches, modifiers = recognize_patterns(problem_desc)
    if matches:
        badges_html = "".join([f'<span class="badge">🔍 Riconosciuto: {m}</span>' for m in matches])
        st.markdown(f"**Pattern rilevati automaticamente:**<br>{badges_html}", unsafe_allow_html=True)
        if modifiers.get('iterative'):
            is_iterativo = True
    else:
        st.caption("Nessun pattern tecnico noto rilevato nella richiesta.")
else:
    matches, modifiers = [], None

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- GENERATION LOGIC -----------------
col_gen, col_empty2 = st.columns([1, 2])
with col_gen:
    generate_btn = st.button("✨ GENERA PROMPT PERFETTO!")

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
        
        # --- 1. CONTEXT ---
        context_parts = [f"Sono un {ruolo}."]
        prefix = ""
        if is_iterativo:
            prefix = modifiers['prefix'] if modifiers and modifiers['prefix'] else "**CONTINUA DAL CODICE PRECEDENTE**\n**MODIFICA:**"
            context_parts.append("Stiamo lavorando in modo iterativo su una codebase esistente. Usa il prefisso richiesto.")
        context = " ".join(context_parts)
        
        # --- 2. OBJECTIVE ---
        objective = f"Obiettivo principale: {obiettivo}\nRichiesta specifica: {problem_desc}"
        if prefix:
            objective = f"{prefix}\n{objective}"
            
        # --- 3. STYLE & STACK ---
        stack = []
        if framework != "Nessuno in particolare":
            stack.append(framework)
        if modifiers and modifiers['framework'] and framework.lower() not in [f.lower() for f in modifiers['framework']]:
            stack.extend(modifiers['framework'])
            
        styles = []
        if stack:
            styles.append(f"Framework suggerito: {', '.join(stack)}.")
        if modifiers and modifiers['libs']:
            styles.append(f"Librerie obbligatorie: {', '.join(modifiers['libs'])}.")
        if modifiers and modifiers['api']:
            styles.append(f"Integrazioni API: {', '.join(modifiers['api'])}.")
            
        if dettaglio >= 80:
            styles.append("Scrivi un codice altamente modulare, con type hints, docstrings per ogni funzione e gestione rigorosa delle eccezioni. Spiega le scelte architetturali.")
        elif dettaglio <= 40:
            styles.append("Vai dritto al sodo: voglio codice super compatto e funzionante. Evita spiegazioni prolisse.")
        else:
            styles.append("Mantieni un codice pulito, leggibile e commentato nei punti chiave.")
            
        style_str = " ".join(styles) if styles else "Codice pulito, best practices moderne."
        
        # --- 4. TONE ---
        tone = "Tecnico, diretto e formale. Evita convenevoli."
        
        # --- 5. AUDIENCE ---
        audience = "Un AI assistant che parla a uno sviluppatore esperto. Evita le banalità."
        
        # --- 6. RESPONSE ---
        response_fmt = f"Rispondi in lingua {lingua}."
        if "streamlit" in [s.lower() for s in stack]:
            response_fmt += " Restituisci il codice completo in un unico file `app.py` pronto da eseguire. Includi il comando `pip install` se necessario."
        else:
            response_fmt += " Restituisci il codice formattato in markdown."
            
        if "tabell" in problem_desc.lower() or (modifiers and "pandas" in modifiers['libs']):
            response_fmt += " Usa tabelle Markdown per spiegare la struttura dei dati o i parametri."
            
        final_prompt = f"""# CONTEXT (Contesto)
{context}

# OBJECTIVE (Obiettivo)
{objective}

# STYLE (Stile e Stack)
{style_str}

# TONE (Tono)
{tone}

# AUDIENCE (Target)
{audience}

# RESPONSE (Formato)
{response_fmt}"""

        # --- SCORING SYSTEM ---
        s_setup = 20 if (modifiers and modifiers['libs']) or stack else 0
        s_table = 15 if ("tabell" in problem_desc.lower() or (modifiers and "pandas" in modifiers['libs'])) else 0
        s_fewshot = 20 if is_iterativo else 0
        s_specs = 25 if len(problem_desc.split()) > 8 else 10
        s_tokens = 20 if 40 <= len(final_prompt.split()) <= 250 else 15
        
        score = s_setup + s_table + s_fewshot + s_specs + s_tokens
        score = min(score, 100)
        
        if score > 90:
            st.session_state.high_score_count += 1
            if st.session_state.high_score_count >= 5:
                st.balloons()
                st.success("🏆 Prompt Master! Hai superato lo score di >90 per 5 volte di fila!")
                st.session_state.high_score_count = 0  # Reset for fun
        
        # ----------------- OUTPUT UI -----------------
        st.markdown("---")
        
        # Copy to clipboard toast simulation
        st.toast("Prompt generato e ottimizzato con successo! 🚀", icon="✅")
        
        col_res1, col_res2 = st.columns([1.6, 1])
        
        with col_res1:
            st.markdown("### ✅ Prompt Generato (Copia questo!)")
            st.code(final_prompt, language="markdown")
            
        with col_res2:
            st.markdown(f"### ⭐ Score: {score}/100")
            
            st.markdown(f"- **Setup eseguibile:** {s_setup}/20")
            st.markdown(f"- **Tabelle usate:** {s_table}/15")
            st.markdown(f"- **Few-shot examples:** {s_fewshot}/20")
            st.markdown(f"- **Specifiche tecniche:** {s_specs}/25")
            st.markdown(f"- **Token ottimale:** {s_tokens}/20")
            
            if score < 100:
                suggestions = []
                if s_table == 0: suggestions.append("richiedi l'output a tabelle")
                if s_fewshot == 0: suggestions.append("attiva l'approccio iterativo")
                if s_setup == 0: suggestions.append("inserisci framework/librerie specifiche")
                if s_specs < 25: suggestions.append("aggiungi più dettagli tecnici")
                
                st.info(f"💡 **Regola d'oro mancante:** Per massimizzare lo score, prova a: {', '.join(suggestions)}")
                
        # CO-STAR Breakdown Table
        st.markdown("### 📋 CO-STAR Preview")
        costar_df = [
            {"Sezione": "Context", "Contenuto": context},
            {"Sezione": "Objective", "Contenuto": objective},
            {"Sezione": "Style", "Contenuto": style_str},
            {"Sezione": "Tone", "Contenuto": tone},
            {"Sezione": "Audience", "Contenuto": audience},
            {"Sezione": "Response", "Contenuto": response_fmt}
        ]
        st.dataframe(pd.DataFrame(costar_df), use_container_width=True, hide_index=True)
