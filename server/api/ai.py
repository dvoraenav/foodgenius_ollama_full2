from fastapi import APIRouter
from pydantic import BaseModel
from services.ollama_client import ollama_generate
from services.external_recipe_service import get_external_recipe_by_id

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
            ingredients = rec.get("ingredients") or []  # list[dict]
            steps = rec.get("steps") or []              # list[str]

            ing_txt = ", ".join(
                f"{i.get('name','')}{(' ' + (i.get('amount') or '')) if i.get('amount') else ''}".strip()
                for i in ingredients if i.get('name')
            )
            steps_txt = " ".join(steps) if isinstance(steps, list) else str(steps)

            ctx = f"Recipe: {title}\nIngredients: {ing_txt}\nSteps: {steps_txt}\n\n"

    # עדיף באנגלית כדי להתאים ל־UI
    sys = "You are a professional cooking assistant. Answer briefly, clearly and practically."
    answer = await ollama_generate(prompt=ctx + req.question, system=sys, temperature=0.3)
    return {"answer": answer}
