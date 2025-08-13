from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
try:
    from server.services.recipe_provider import get_recipe_by_id
    from server.services.transformer import veganize, scale
    from server.services.ollama_client import ollama_generate
except ModuleNotFoundError:
    from services.recipe_provider import get_recipe_by_id
    from services.transformer import veganize, scale
    from services.ollama_client import ollama_generate

router = APIRouter()

class TransformReq(BaseModel):
    recipe_id: str
    goal: str               # "veganize" | "scale"
    servings_from: float | None = None
    servings_to: float | None = None
    use_llm: bool = False

@router.post("/transform")
async def transform(req: TransformReq):
    rec = get_recipe_by_id(req.recipe_id)
    if not rec: raise HTTPException(404, "Recipe not found")
    if req.goal == "veganize":
        if req.use_llm:
            sys = "את יועצת קולינרית. החזירי JSON בלבד עם title, ingredients(list), steps(list)."
            prompt = f"""הפוך את המתכון הבא לטבעוני. שמור על סגנון. החזר JSON בלבד.
כותרת: {rec.get('title')}
מרכיבים: {', '.join(i.get('name','') for i in rec.get('ingredients',[]))}
שלבים: {', '.join(rec.get('steps',[]))}
"""
            txt = await ollama_generate(prompt, system=sys, temperature=0.2)
            import json
            try: return {"result": json.loads(txt), "source": "llm"}
            except Exception: return {"result": {"title": rec.get("title")+" (טבעוני/LLM)", "raw": txt}, "source": "llm-raw"}
        return {"result": veganize(rec), "source": "rules"}
    if req.goal == "scale":
        if not (req.servings_from and req.servings_to): raise HTTPException(400, "servings_from/to required for scale")
        factor = float(req.servings_to) / float(req.servings_from)
        return {"result": scale(rec, factor), "source": "rules"}
    raise HTTPException(400, "unknown goal")

class ChatReq(BaseModel):
    recipe_id: str | None = None
    question: str

@router.post("/chat")
async def chat(req: ChatReq):
    ctx = ""
    if req.recipe_id:
        rec = get_recipe_by_id(req.recipe_id)
        if rec:
            ing = "; ".join(f"{i.get('name')} {i.get('amount','')} {i.get('unit','')}".strip()
                            for i in rec.get("ingredients", []))
            steps = " ".join(rec.get("steps", []))
            ctx = f"מתכון: {rec.get('title')}\nמרכיבים: {ing}\nשלבים: {steps}\n\n"
    sys = "את שף/ית ועוזרת בישול מקצועית. עני קצר, ברור ומעשי."
    answer = await ollama_generate(prompt=ctx + req.question, system=sys, temperature=0.3)
    return {"answer": answer}
