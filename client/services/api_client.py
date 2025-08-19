import requests
from config import API_BASE_URL
from services.auth import AUTH

class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if AUTH.token:
            headers["Authorization"] = f"Bearer {AUTH.token}"
        return headers

    def get(self, path: str, params=None):
        r = requests.get(self.base_url + path, params=params, headers=self._headers(), timeout=20)
        if not r.ok:
            raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    def post(self, path: str, data=None):
        r = requests.post(self.base_url + path, json=data or {}, headers=self._headers(), timeout=20)
        if not r.ok:
            raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    # --- מתכונים חיצוניים (TheMealDB) ---
    def get_external_recipes(self, query: str):
        return self.get("/recipes/external", {"q": query})

    def get_external_recipe_by_id(self, recipe_id: str):
        return self.get(f"/recipes/external/{recipe_id}")

    # --- AI Chat ---
    def chat(self, question: str, recipe_id: str | None = None):
        return self.post("/ai/chat", {"question": question, "recipe_id": recipe_id})

    # --- הרשמה והתחברות ---
    def register(self, email: str, name: str, password: str):
        return self.post("/auth/register", {"email": email, "name": name, "password": password})

    def login(self, email: str, password: str):
        return self.post("/auth/login", {"email": email, "password": password})
