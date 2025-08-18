from fastapi import APIRouter, HTTPException, Query
from typing import List
try:
    from server.schemas.recipe import RecipeSummary, RecipeDetail
    from server.services.recipe_provider import search_recipes, get_recipe_by_id
except ModuleNotFoundError:
    from schemas.recipe import RecipeSummary, RecipeDetail
    from services.recipe_provider import search_recipes, get_recipe_by_id

router = APIRouter()

@router.get("/search", response_model=List[RecipeSummary])
def search(q: str = Query("", description="Ingredients or keywords, comma/space separated"),
           mode: str = Query("AND"), min_k: int = Query(1), limit: int = Query(30)):
    return search_recipes(q, limit=limit, mode=mode, min_k=min_k)

@router.get("/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: str):
    rec = get_recipe_by_id(recipe_id)
    if not rec: raise HTTPException(404, "Recipe not found")
    return rec