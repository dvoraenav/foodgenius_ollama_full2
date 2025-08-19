from fastapi import APIRouter
from pydantic import BaseModel
from services.ollama_client import ollama_generate
from services.external_recipe_service import get_external_recipe_by_id  # <- דוגמה לפונקציה שניגשת למתכונים

router = APIRouter()

class ChatReq(BaseModel):
    recipe_id: str | None = None
    question: str

@router.post("/chat")
async def chat(req: ChatReq):
    ctx = ""
    if req.recipe_id:
        rec = get_external_recipe_by_id(req.recipe_id)
        if rec:
            title = rec.get("title", "")
            ing = rec.get("ingredients", "")
            steps = rec.get("instructions", "")
            ctx = f"מתכון: {title}\nמרכיבים: {ing}\nשלבים: {steps}\n\n"

    sys = "את שף/ית ועוזרת בישול מקצועית. עני קצר, ברור ומעשי."
    answer = await ollama_generate(prompt=ctx + req.question, system=sys, temperature=0.3)
    return {"answer": answer}
