from fastapi import APIRouter, HTTPException
from typing import List, Dict
from services.nutrition_api_service import NutritionAPIService

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

@router.post("/calculate")
async def calculate_nutrition(ingredients: List[Dict]):
    """
    Calculate nutrition data from ingredients using API-Ninjas
    
    Body: List of ingredients from TheMealDB format
    Returns: Nutrition data (calories, protein, carbs, fat)
    """
    try:
        nutrition_service = NutritionAPIService()
        result = nutrition_service.get_nutrition_from_ingredients(ingredients)
        
        if result:
            return {
                "success": True,
                "data": result,
                "source": "api-ninjas"
            }
        else:
            # Fallback to local estimation
            from services.nutrition_api_service import _calculate_nutrition_locally
            local_result = _calculate_nutrition_locally(ingredients)
            return {
                "success": True,
                "data": local_result,
                "source": "local-estimation"
            }
            
    except Exception as e:
        print(f"Nutrition calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating nutrition: {str(e)}")

@router.get("/test")
async def test_api_connection():
    """Test API-Ninjas connection"""
    try:
        nutrition_service = NutritionAPIService()
        is_connected = nutrition_service.test_connection()
        
        return {
            "api_available": is_connected,
            "api_key_configured": nutrition_service.api_key is not None
        }
    except Exception as e:
        return {
            "api_available": False,
            "error": str(e)
        }