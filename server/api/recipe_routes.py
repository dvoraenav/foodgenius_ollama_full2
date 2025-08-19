"""exposes GET /recipes/external endpoint to search recipes from TheMealDB via external_recipe_service"""

from fastapi import APIRouter, Query
from  services.external_recipe_service import get_external_recipes, get_external_recipe_by_id  # ודאי שהשורה נראית ככה

router = APIRouter()

# היה: @router.get("/recipes/external")
@router.get("/external")
def fetch_external_recipes(q: str = Query(...)):
    return get_external_recipes(q)

# היה: @router.get("/recipes/external/{rid}")
@router.get("/external/{rid}")
def fetch_external_recipe_by_id(rid: str):
    return get_external_recipe_by_id(rid)