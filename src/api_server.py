import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from src.core.pattern_engine import PatternEngine
from src.core.agent_workflow import MultiAgentRevisor
from src.core.db_manager import PromptDBManager
from src.prompt_generator import generate_costar
from src.utils.score import calculate_score

# Configurazione logging server
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PromptDoctor API", version="1.0.0")

# Abilitiamo CORS a beneficio di futuri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Inizializzazione Core...")
engine = PatternEngine()
revisor = MultiAgentRevisor()
db_manager = PromptDBManager()
logger.info("Core Module Singleton istanziati assieme al server FastAPI.")

class GeneratePromptRequest(BaseModel):
    problem_desc: str = Field(..., description="Descrizione del problema")
    use_ai: bool = False
    obiettivo: str
    ruolo: str
    framework: str
    lingua: str
    dettaglio: str
    is_iterativo: bool
    custom_context: str = ""

class AnalyzeTextRequest(BaseModel):
    problem_desc: str
    use_ai: bool = False
    custom_context: str = ""

@app.post("/api/analyze_text")
async def analyze_text_endpoint(req: AnalyzeTextRequest):
    try:
        matches, modifiers, used_ai = engine.analyze_text(
            req.problem_desc, 
            use_ai=req.use_ai, 
            custom_context=req.custom_context
        )
        return {
            "matches": matches,
            "modifiers": modifiers,
            "used_ai": used_ai
        }
    except Exception as e:
        logger.error(f"Errore su analyze_text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_prompt")
async def generate_prompt_endpoint(req: GeneratePromptRequest):
    try:
        matches, modifiers, used_ai = engine.analyze_text(
            req.problem_desc, 
            use_ai=req.use_ai, 
            custom_context=req.custom_context
        )
        
        stack = []
        if req.framework != "Nessuno in particolare":
            stack.append(req.framework)
        if modifiers and modifiers.get('framework') and req.framework.lower() not in [f.lower() for f in modifiers['framework']]:
            stack.extend(list(modifiers['framework']))
            
        final_problem_desc = req.problem_desc
        score_ai = None
        giudizio_critico = None
        
        if req.use_ai:
            # Essendo un API Request, non stiamo mappando container interattivi
            ai_result = revisor.rewrite_text(req.problem_desc)
            final_problem_desc = ai_result.get("text", req.problem_desc)
            score_ai = ai_result.get("score_ai", 70)
            giudizio_critico = ai_result.get("giudizio_critico", "")
            
        prompt_data = generate_costar(
            req.obiettivo, req.ruolo, req.framework, req.lingua, req.dettaglio, 
            req.is_iterativo, final_problem_desc, modifiers, stack
        )
        
        tokens = len(prompt_data['final'].split())
        score_data = calculate_score(
            req.problem_desc, modifiers, stack, req.is_iterativo, 
            tokens, used_ai, ai_judge_score=score_ai
        )
        
        db_manager.save_prompt(
            original_input=req.problem_desc, 
            generated_prompt=prompt_data['final'], 
            score=score_data['total']
        )
        
        return {
            "final_prompt": prompt_data['final'],
            "final_problem_desc": final_problem_desc,
            "score": score_data['total'],
            "score_data": score_data,
            "costar_data": prompt_data,
            "matches": matches,
            "modifiers": modifiers,
            "giudizio_critico": giudizio_critico
        }

    except Exception as e:
        logger.error(f"Errore su generate_prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    return db_manager.get_all_prompts()

if __name__ == "__main__":
    uvicorn.run("src.api_server:app", host="0.0.0.0", port=8000, reload=True)
