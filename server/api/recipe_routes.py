"""exposes GET /recipes/external endpoint to search recipes from TheMealDB via external_recipe_service"""

from fastapi import APIRouter, Query
from services.external_recipe_service import get_external_recipes, get_external_recipe_by_id
from services.cloudinary_service import cloudinary_service

router = APIRouter()

# היה: @router.get("/recipes/external")
@router.get("/external")
def fetch_external_recipes(q: str = Query(...)):
    return get_external_recipes(q)

# היה: @router.get("/recipes/external/{rid}")
@router.get("/external/{rid}")
def fetch_external_recipe_by_id(rid: str):
    return get_external_recipe_by_id(rid)

# הוספה חדשה: endpoint ללוגו
@router.get("/logo")
def get_logo_url(width: int = Query(default=120), height: int = Query(default=40)):
    """מחזיר URL ללוגו של FoodGenius מ-Cloudinary"""
    try:
        logo_url = cloudinary_service.get_logo_url(width=width, height=height)
        return {"logo_url": logo_url, "status": "success"}
    except Exception as e:
        return {"logo_url": "", "status": "error", "message": str(e)}