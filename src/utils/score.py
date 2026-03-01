from typing import Dict, Any, List

def calculate_score(
    problem_desc: str, 
    modifiers: Dict[str, Any], 
    stack: List[str], 
    is_iterativo: bool, 
    prompt_tokens: int,
    used_ai: bool = False,
    ai_judge_score: int = None
) -> Dict[str, Any]:
    """
    Calculate the gamified prompt score.
    Returns a dictionary with partial scores, total score, and suggestions for improvement.
    """
    
    # 1. Setup/Libraries Score
    s_setup = 20 if (modifiers and modifiers.get('libs')) or stack else 0
    
    # 2. Tables/Data Structures Score
    s_table = 15 if ("tabell" in problem_desc.lower() or (modifiers and "pandas" in modifiers.get('libs', []))) else 0
    
    # 3. Few-shot / Iteration Score
    s_fewshot = 20 if is_iterativo else 0
    
    # 4. Specifications/Detail Score
    s_specs = 25 if len(problem_desc.split()) > 8 else 10
    
    # 5. Token Optimization Score
    s_tokens = 20 if 40 <= prompt_tokens <= 250 else 15
    
    # 6. AI Bonus!
    s_ai_bonus = 10 if used_ai and modifiers else 0

    score = s_setup + s_table + s_fewshot + s_specs + s_tokens + s_ai_bonus
    score = min(score, 100) # Cap at 100

    if ai_judge_score is not None:
        # Weighted Average: 60% AI, 40% Rules
        score = int((ai_judge_score * 0.6) + (score * 0.4))
        score = min(max(score, 0), 100)

    suggestions = []
    if s_table == 0: suggestions.append("richiedi l'output a tabelle")
    if s_fewshot == 0: suggestions.append("attiva l'approccio iterativo")
    if s_setup == 0: suggestions.append("inserisci framework/librerie specifiche o usa l'AI")
    if s_specs < 25: suggestions.append("aggiungi più dettagli tecnici")

    return {
        "total": score,
        "setup": s_setup,
        "table": s_table,
        "fewshot": s_fewshot,
        "specs": s_specs,
        "tokens": s_tokens,
        "ai_bonus": s_ai_bonus,
        "suggestions": suggestions
    }
