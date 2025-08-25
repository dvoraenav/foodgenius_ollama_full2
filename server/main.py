import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api import recipe_routes
from api.nutrition import router as nutrition_router

load_dotenv()
load_dotenv()
print(f"DEBUG: CLOUDINARY_URL = {os.getenv('CLOUDINARY_URL')}")
print(f"DEBUG: API_NINJAS_KEY = {os.getenv('API_NINJAS_KEY')}") 

try:
    from api import auth, ai
    from server.infrastructure.db import init_db
except ModuleNotFoundError:
    from api import auth, ai
    from infrastructure.db import init_db

app = FastAPI(title="FoodGenius API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(recipe_routes.router, prefix="/recipes", tags=["recipes"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(nutrition_router) 

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/test-cloudinary")
def test_cloudinary():
    from services.cloudinary_service import cloudinary_service
    debug_info = cloudinary_service.debug_info()
    logo_url = cloudinary_service.get_logo_url(120, 40)
    return {
        "debug_info": debug_info,
        "logo_url": logo_url
    }