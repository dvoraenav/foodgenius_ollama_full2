import os
from urllib.parse import quote
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")
CLOUD = CLOUDINARY_URL.rsplit("@", 1)[1] if CLOUDINARY_URL else ""
def url(public_id: str, w: int = 600, h: int = 400, fit: str = "fill") -> str | None:
    if not public_id or not CLOUD: return None
    return f"https://res.cloudinary.com/{CLOUD}/image/upload/c_{fit},w_{w},h_{h}/{quote(public_id)}.jpg"
