"""
Configuration file for PromptDoctor PRO.
Contains CSS styling, static tech patterns fallback, and generic constants.
"""

CSS_THEME = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

/* Apply API Background Image to the App container and fallback to gradient */
.stApp {
    background: linear-gradient(rgba(14, 17, 23, 0.85), rgba(14, 17, 23, 0.95)),
                url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop") no-repeat center center fixed;
    background-size: cover;
    color: #f1f2f6;
    font-family: 'Outfit', sans-serif !important;
}

/* Base text styling for better contrast */
p, label, li, span, div {
    color: #e2e8f0 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

/* Sidebar Styling - Glassmorphism */
[data-testid="stSidebar"] {
    background: rgba(30, 33, 48, 0.45) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Enhance Headers */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    letter-spacing: -0.5px;
}

/* Title Gradient highlight */
.gradient-text {
    background: -webkit-linear-gradient(45deg, #34d399, #10b981, #059669);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none !important;
    display: inline-block;
}

/* Re-styled Buttons */
.stButton>button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.stButton>button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 20px rgba(16, 185, 129, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.4);
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.4);
}

/* Glass Box Container */
.glass-box {
    background: rgba(20, 24, 39, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    margin-bottom: 24px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.4em 0.8em;
    font-size: 0.85em;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15));
    color: #6ee7b7 !important;
    border: 1px solid rgba(110, 231, 183, 0.3);
    margin-right: 8px;
    margin-bottom: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    text-shadow: none !important;
}

.badge-ai {
    display: inline-block;
    padding: 0.4em 0.8em;
    font-size: 0.85em;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(94, 234, 212, 0.15), rgba(45, 212, 191, 0.15));
    color: #5eead4 !important;
    border: 1px solid rgba(94, 234, 212, 0.3);
    margin-right: 8px;
    margin-bottom: 8px;
    box-shadow: 0 2px 10px rgba(45, 212, 191, 0.15);
    text-shadow: none !important;
    animation: pulse-glow 2s infinite alternate;
}

@keyframes pulse-glow {
    0% { box-shadow: 0 0 5px rgba(94, 234, 212, 0.2); }
    100% { box-shadow: 0 0 15px rgba(94, 234, 212, 0.5); }
}

/* Input Fields Overrides */
div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
    background-color: rgba(15, 23, 42, 0.6) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}

div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
}

/* Make placeholders readable */
::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

/* Custom stInfo and stSuccess borders */
[data-testid="stAlert"] {
    background-color: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    color: #e2e8f0 !important;
}

/* Dataframe header colors */
thead tr th {
    background-color: rgba(30, 41, 59, 0.8) !important;
    color: #10b981 !important;
    font-weight: bold;
}
</style>
"""

STATIC_TECH_PATTERNS = {
    r"(barcode|qr|code|qr\s*code|qr-code)": {"libs": "treepoem pillow qrcode faker pyzbar opencv-python", "framework": "streamlit"},
    r"(web app|streamlit|ui|dashboard)": {"framework": "streamlit", "ui": "st.sidebar st.image st.button"},
    r"(modifica|update|fix|change|aggiorna|correggi)": {"iterative": True, "prefix": "**CONTINUA DAL CODICE PRECEDENTE**\n**MODIFICA:**"},
    r"(ar|vr|unity|mrtk|xreal|augmented reality)": {"libs": "unity mrtk3 xreal-beam", "platform": "android xr"},
    r"(magic|mtg|deck|cards|scryfall)": {"api": "scryfall", "libs": "pandas requests"},
    r"(cooking|recipe|nutrition|cucina|ricetta)": {"api": "spoonacular", "libs": "pandas nutritionix"},
    r"(fitness|gym|training|strava)": {"libs": "pandas matplotlib py-strava", "data": "strava api"}
}

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"  # Ensure user has pulled this model, e.g. `ollama run llama3.2`
