from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Nutrition(BaseModel):
    cal: float
    protein: float
    fat: float
    carbs: float

class Ingredient(BaseModel):
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None

class RecipeSummary(BaseModel):
    id: str
    title: str
    image: Optional[str] = None
    nutrition: Optional[Nutrition] = None
    tags: Optional[List[str]] = None

class RecipeDetail(RecipeSummary):
    ingredients: List[Ingredient] = []
    steps: List[str] = []
    source: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
