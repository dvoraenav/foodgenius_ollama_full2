import requests
from config import API_BASE_URL
from services.auth import AUTH

class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if AUTH.token: h["Authorization"] = f"Bearer {AUTH.token}"
        return h

    def get(self, path: str, params=None):
        r = requests.get(self.base_url + path, params=params, headers=self._headers(), timeout=20)
        if not r.ok: raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    def post(self, path: str, json=None):
        r = requests.post(self.base_url + path, json=json, headers=self._headers(), timeout=40)
        if not r.ok: raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    def search(self, q: str): return self.get("/recipes/search", {"q": q})
    def recipe(self, rid: str): return self.get(f"/recipes/{rid}")
    def transform(self, payload: dict): return self.post("/ai/transform", payload)
    def transform_llm_vegan(self, rid: str): return self.post("/ai/transform", {"recipe_id": rid, "goal":"veganize", "use_llm": True})
    def chat(self, question: str, recipe_id: str | None = None): return self.post("/ai/chat", {"question": question, "recipe_id": recipe_id})
    def register(self, email, name, password): return self.post("/auth/register", {"email": email, "name": name, "password": password})
    def login(self, email, password): return self.post("/auth/login", {"email": email, "password": password})
