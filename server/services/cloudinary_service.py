import os
import re
from typing import Optional
from urllib.parse import urlparse

class CloudinaryService:
    """
    שירות לניהול תמונות מ-Cloudinary בשרת
    """
    
    def __init__(self):
        # נסה לקרוא CLOUDINARY_URL קודם
        cloudinary_url = os.getenv("CLOUDINARY_URL")
        
        if cloudinary_url:
            # פירוק CLOUDINARY_URL
            self._parse_cloudinary_url(cloudinary_url)
        else:
            # פרטי החיבור מה-.env בנפרד
            self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
            self.api_key = os.getenv("CLOUDINARY_API_KEY")
            self.api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        # ברירת מחדל אם אין cloud_name
        if not self.cloud_name:
            self.cloud_name = "dzowmpqbq"
    
    def _parse_cloudinary_url(self, url: str):
        """פירוק CLOUDINARY_URL לרכיבים"""
        # דוגמה: cloudinary://api_key:api_secret@cloud_name
        match = re.match(r'cloudinary://([^:]+):([^@]+)@(.+)', url)
        if match:
            self.api_key = match.group(1)
            self.api_secret = match.group(2)
            self.cloud_name = match.group(3)
        else:
            print(f"שגיאה בפירוק CLOUDINARY_URL: {url}")
            self.cloud_name = None
            self.api_key = None
            self.api_secret = None
    
    def get_image_url(self, public_id: str, **transformations) -> str:
        """
        יוצר URL לתמונה עם אופציות עיבוד
        """
        if not self.cloud_name:
            return ""
            
        base_url = f"https://res.cloudinary.com/{self.cloud_name}/image/upload"
        
        # בניית string של transformations
        transform_parts = []
        
        if transformations:
            for key, value in transformations.items():
                if key == "width":
                    transform_parts.append(f"w_{value}")
                elif key == "height":
                    transform_parts.append(f"h_{value}")
                elif key == "crop":
                    transform_parts.append(f"c_{value}")
                elif key == "quality":
                    transform_parts.append(f"q_{value}")
                elif key == "format":
                    transform_parts.append(f"f_{value}")
                elif key == "gravity":
                    transform_parts.append(f"g_{value}")
        
        # יצירת URL מלא
        if transform_parts:
            transform_string = ",".join(transform_parts)
            return f"{base_url}/{transform_string}/{public_id}"
        else:
            return f"{base_url}/{public_id}"
    
    def get_logo_url(self, width: Optional[int] = None, height: Optional[int] = None) -> str:
        """מחזיר URL ללוגו של FoodGenius"""
        transformations = {}
        if width:
            transformations["width"] = width
        if height:
            transformations["height"] = height
        if width or height:
            transformations["crop"] = "fit"  # שמירה על יחס גובה-רוחב
            transformations["quality"] = "auto"
        
        return self.get_image_url("foodgenius_logo", **transformations)
    
    def get_recipe_image_url(self, recipe_name: str, width: int = 300, height: int = 200) -> str:
        """
        מחזיר URL לתמונת מתכון בהתאם לסוג המתכון
        """
        # רשימת תמונות מתכונים
        recipe_images = {
            "pasta": "recipe_pasta",
            "pizza": "recipe_pizza", 
            "cake": "recipe_cake",
            "salad": "recipe_salad",
            "soup": "recipe_soup",
            "chicken": "recipe_chicken",
            "fish": "recipe_fish",
            "bread": "recipe_bread",
            "dessert": "recipe_dessert",
            "vegetarian": "recipe_vegetarian"
        }
        
        # חיפוש מילת מפתח בשם המתכון
        recipe_name_lower = recipe_name.lower()
        selected_image = "recipe_placeholder"  # ברירת מחדל
        
        for keyword, image_id in recipe_images.items():
            if keyword in recipe_name_lower:
                selected_image = image_id
                break
        
        return self.get_image_url(
            selected_image,
            width=width,
            height=height,
            crop="fill",
            quality="auto"
        )
    
    def debug_info(self):
        """מחזיר מידע debug על החיבור"""
        return {
            "cloud_name": self.cloud_name,
            "has_api_key": bool(self.api_key),
            "has_api_secret": bool(self.api_secret),
            "cloudinary_url_exists": bool(os.getenv("CLOUDINARY_URL"))
        }

# יצירת instance יחיד לשימוש בכל הפרויקט
cloudinary_service = CloudinaryService()