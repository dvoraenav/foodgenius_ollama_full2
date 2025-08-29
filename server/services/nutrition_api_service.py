# # server/services/nutrition_api_service.py
# import requests
# import os
# from typing import List, Dict, Optional
# from dotenv import load_dotenv

# load_dotenv()

# class NutritionAPIService:
#     def __init__(self):
#         self.api_key = os.getenv("API_NINJAS_KEY")  # Add to .env file
#         self.base_url = "https://api.api-ninjas.com/v1/nutrition"
        
#     def get_nutrition_from_ingredients(self, ingredients: List[Dict]) -> Optional[Dict]:
#         """
#         Get real nutrition data from API-Ninjas based on recipe ingredients
        
#         Args:
#             ingredients: List of ingredient objects from TheMealDB
            
#         Returns:
#             Dict with calories, protein, carbs, fat or None if error
#         """
#         if not self.api_key:
#             print("API-Ninjas API key not found in environment variables")
#             return None
            
#         try:
#             # Build query string from ingredients
#             query_parts = []
#             for ingredient in ingredients[:10]:  # Limit to 10 ingredients to avoid long queries
#                 name = ingredient.get('name', '').strip()
#                 amount = ingredient.get('amount', '').strip()
                
#                 if name:
#                     # Format: "amount ingredient_name" or just "ingredient_name"
#                     if amount and amount.lower() not in ['', 'to taste', 'as needed']:
#                         query_parts.append(f"{amount} {name}")
#                     else:
#                         query_parts.append(name)
            
#             if not query_parts:
#                 return None
                
#             # Join ingredients with " and "
#             query = " and ".join(query_parts)
            
#             # Limit query length (API has 1500 char limit)
#             if len(query) > 1400:
#                 query = query[:1400]
            
#             print(f"Nutrition API query: {query}")
            
#             # Make API request
#             headers = {
#                 'X-Api-Key': self.api_key
#             }
            
#             response = requests.get(
#                 f"{self.base_url}?query={query}", 
#                 headers=headers,
#                 timeout=10
#             )
            
#             if response.status_code == 200:
#                 data = response.json()
#                 return self._process_nutrition_response(data)
#             else:
#                 print(f"API-Ninjas error: {response.status_code} - {response.text}")
#                 return None
                
#         except Exception as e:
#             print(f"Error calling nutrition API: {e}")
#             return None
    
#     def _process_nutrition_response(self, data: List[Dict]) -> Dict:
#         """
#         Process API-Ninjas response and sum up all ingredients
        
#         Args:
#             data: List of nutrition objects from API
            
#         Returns:
#             Dict with total calories, protein, carbs, fat
#         """
#         total_calories = 0
#         total_protein = 0
#         total_carbs = 0
#         total_fat = 0
        
#         for item in data:
#             # Safely convert to float, handle strings and None values
#             try:
#                 calories = float(item.get('calories', 0) or 0)
#                 protein = float(item.get('protein_g', 0) or 0)
#                 carbs = float(item.get('carbohydrates_total_g', 0) or 0)
#                 fat = float(item.get('fat_total_g', 0) or 0)
                
#                 total_calories += calories
#                 total_protein += protein
#                 total_carbs += carbs
#                 total_fat += fat
                
#             except (ValueError, TypeError) as e:
#                 print(f"Error processing nutrition item {item}: {e}")
#                 continue
        
#         return {
#             'calories': int(total_calories),
#             'protein': int(total_protein),
#             'carbs': int(total_carbs),
#             'fat': int(total_fat)
#         }
    
#     def test_connection(self) -> bool:
#         """Test if API connection works"""
#         try:
#             headers = {'X-Api-Key': self.api_key}
#             response = requests.get(
#                 f"{self.base_url}?query=1 apple", 
#                 headers=headers,
#                 timeout=5
#             )
#             return response.status_code == 200
#         except:
#             return False


# # Updated nutrition calculation function that tries API first, falls back to local
# def calculate_nutrition_from_ingredients(ingredients: List[Dict]) -> Dict:
#     """
#     Calculate nutrition data - tries API-Ninjas first, falls back to local estimation
    
#     Args:
#         ingredients: List of ingredient objects
        
#     Returns:
#         Dict with calories, protein, carbs, fat
#     """
#     # Try API-Ninjas first
#     nutrition_service = NutritionAPIService()
#     api_result = nutrition_service.get_nutrition_from_ingredients(ingredients)
    
#     if api_result and api_result['calories'] > 0:
#         print("Using real nutrition data from API-Ninjas")
#         return api_result
    
#     # Fallback to local estimation
#     print("Falling back to local nutrition estimation")
#     return _calculate_nutrition_locally(ingredients)


# def _calculate_nutrition_locally(ingredients: List[Dict]) -> Dict:
#     """
#     Local nutrition estimation (same as before)
#     """
#     nutrition_db = {
#         'flour': {'cal': 364, 'protein': 10, 'carbs': 76, 'fat': 1},
#         'egg': {'cal': 155, 'protein': 13, 'carbs': 1, 'fat': 11},
#         'milk': {'cal': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1},
#         'sugar': {'cal': 387, 'protein': 0, 'carbs': 100, 'fat': 0},
#         'oil': {'cal': 884, 'protein': 0, 'carbs': 0, 'fat': 100},
#         'butter': {'cal': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81},
#         'chicken': {'cal': 239, 'protein': 27, 'carbs': 0, 'fat': 14},
#         'garlic': {'cal': 149, 'protein': 6.4, 'carbs': 33, 'fat': 0.5},
#         'onion': {'cal': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1},
#         'tomato': {'cal': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2},
#         'rice': {'cal': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
#         'potato': {'cal': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1},
#     }
    
#     total_cal = 0
#     total_protein = 0
#     total_carbs = 0
#     total_fat = 0
#     found_ingredients = 0
    
#     for ingredient in ingredients:
#         name = ingredient.get('name', '').lower()
        
#         for key, values in nutrition_db.items():
#             if key in name:
#                 found_ingredients += 1
#                 # Estimate portions based on ingredient type
#                 if key in ['flour']:
#                     portion_factor = 1.0
#                 elif key in ['egg']:
#                     portion_factor = 0.5
#                 elif key in ['milk']:
#                     portion_factor = 3.0
#                 elif key in ['sugar']:
#                     portion_factor = 0.2
#                 elif key in ['oil', 'butter']:
#                     portion_factor = 0.15
#                 elif key in ['chicken', 'rice', 'potato']:
#                     portion_factor = 1.5
#                 else:
#                     portion_factor = 0.1
                
#                 total_cal += values['cal'] * portion_factor
#                 total_protein += values['protein'] * portion_factor
#                 total_carbs += values['carbs'] * portion_factor
#                 total_fat += values['fat'] * portion_factor
#                 break
    
#     if found_ingredients == 0:
#         return {'calories': 300, 'protein': 20, 'carbs': 35, 'fat': 12}
    
#     return {
#         'calories': int(total_cal),
#         'protein': int(total_protein),
#         'carbs': int(total_carbs),
#         'fat': int(total_fat)
#     }