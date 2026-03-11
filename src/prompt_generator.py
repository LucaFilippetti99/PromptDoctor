from typing import Dict, Any, List

def generate_costar(
    obiettivo: str,
    ruolo: str,
    framework: str,
    lingua: str,
    dettaglio: int,
    is_iterativo: bool,
    problem_desc: str,
    modifiers: Dict[str, Any],
    stack: List[str]
) -> Dict[str, str]:
    """Generates the final CO-STAR prompt and its parts."""
    
    # --- 1. CONTEXT ---
    context_parts = [f"Sono un {ruolo}."]
    prefix = ""
    if is_iterativo:
        prefix = modifiers['prefix'] if modifiers and modifiers.get('prefix') else "**CONTINUA DAL CODICE PRECEDENTE**\n**MODIFICA:**"
        context_parts.append("Stiamo lavorando in modo iterativo su una codebase esistente. Usa il prefisso richiesto.")
    context = " ".join(context_parts)
    
    # --- 2. OBJECTIVE ---
    objective = f"Obiettivo principale: {obiettivo}\nRichiesta specifica: {problem_desc}"
    if prefix:
        objective = f"{prefix}\n{objective}"
        
    # --- 3. STYLE & STACK ---
    styles = []
    if stack:
        styles.append(f"Framework suggerito: {', '.join(stack)}.")
    if modifiers and modifiers.get('libs'):
        styles.append(f"Librerie obbligatorie: {', '.join(modifiers['libs'])}.")
    if modifiers and modifiers.get('api'):
        styles.append(f"Integrazioni API: {', '.join(modifiers['api'])}.")
        
    dettaglio_val = int(dettaglio) if str(dettaglio).isdigit() else 50
    if dettaglio_val >= 80:
        styles.append("Scrivi un codice altamente modulare, con type hints, docstrings per ogni funzione e gestione rigorosa delle eccezioni. Spiega le scelte architetturali.")
    elif dettaglio_val <= 40:
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
    
    frameworks_lower = [s.lower() for s in stack]
    if "streamlit" in frameworks_lower or "flask" in frameworks_lower or "react" in frameworks_lower:
        response_fmt += " Restituisci il codice completo in un unico script/file pronto da eseguire (es. `app.py`). Includi il comando `pip install` o `npm install` se testabile."
    else:
        response_fmt += " Restituisci il codice formattato in markdown."
        
    if "tabell" in problem_desc.lower() or (modifiers and "pandas" in modifiers.get('libs', [])):
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

    return {
        "context": context,
        "objective": objective,
        "style": style_str,
        "tone": tone,
        "audience": audience,
        "response": response_fmt,
        "final": final_prompt
    }
