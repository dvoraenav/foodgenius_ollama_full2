import os
import re
from typing import Optional

class CloudinaryService:
    """שירות לניהול תמונות מ-Cloudinary בשרת"""
    
    def __init__(self):
        cloudinary_url = os.getenv("CLOUDINARY_URL")
        
        if cloudinary_url:
            self._parse_cloudinary_url(cloudinary_url)
        else:
            self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
            self.api_key = os.getenv("CLOUDINARY_API_KEY")
            self.api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if not self.cloud_name:
            self.cloud_name = "dzowmpqbq"
    
    def _parse_cloudinary_url(self, url: str):
        """פירוק CLOUDINARY_URL לרכיבים"""
        match = re.match(r'cloudinary://([^:]+):([^@]+)@(.+)', url)
        if match:
            self.api_key = match.group(1)
            self.api_secret = match.group(2)
            self.cloud_name = match.group(3)
        else:
            self.cloud_name = None
            self.api_key = None
            self.api_secret = None
    
    def get_image_url(self, public_id: str, **transformations) -> str:
        """יוצר URL לתמונה עם אופציות עיבוד"""
        if not self.cloud_name:
            return ""
            
        base_url = f"https://res.cloudinary.com/{self.cloud_name}/image/upload"
        
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
            transformations["crop"] = "fit"
            transformations["quality"] = "auto"
        
        return self.get_image_url("foodgenius_logo", **transformations)

# יצירת instance יחיד לשימוש בכל הפרויקט
cloudinary_service = CloudinaryService()