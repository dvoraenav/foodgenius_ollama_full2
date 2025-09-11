import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api import recipe_routes
from api.orders import router as orders_router

load_dotenv()

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
app.include_router(orders_router, prefix="/orders", tags=["orders"])

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
