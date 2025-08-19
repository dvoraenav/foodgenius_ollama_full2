import requests

def get_external_recipes(query: str):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    r = requests.get(url, timeout=20); r.raise_for_status()
    meals = r.json().get("meals") or []
    return [_adapt(meal) for meal in meals]

def get_external_recipe_by_id(rid: str):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={rid}"
    r = requests.get(url, timeout=20); r.raise_for_status()
    meals = r.json().get("meals") or []
    return _adapt(meals[0]) if meals else None

def _adapt(meal: dict):
    ingredients = [
        {
            "name": (meal.get(f"strIngredient{i}") or "").strip(),
            "amount": (meal.get(f"strMeasure{i}") or "").strip(),
            "unit": "",
        }
        for i in range(1, 21)
        if (meal.get(f"strIngredient{i}") or "").strip()
    ]
    steps = (meal.get("strInstructions") or "").strip().split("\r\n")
    steps = [s for s in steps if s]
    return {
        "id": meal["idMeal"],
        "title": meal["strMeal"],
        "image": meal["strMealThumb"],
        "tags": (meal.get("strTags") or "").split(",") if meal.get("strTags") else [],
        "nutrition": {"cal": 300, "protein": "?", "fat": "?", "carbs": "?"},  # placeholder
        "ingredients": ingredients,
        "steps": steps,
        "source": meal.get("strSource"),
    }
