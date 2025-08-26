import requests
from config import API_BASE_URL
from services.auth import AUTH

DEFAULT_TIMEOUT = 20

class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if AUTH.token:
            headers["Authorization"] = f"Bearer {AUTH.token}"
        return headers

    def get(self, path: str, params=None, timeout: int = DEFAULT_TIMEOUT):
        r = requests.get(self.base_url + path, params=params, headers=self._headers(), timeout=timeout)
        if not r.ok:
            raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    def post(self, path: str, json=None, timeout: int = DEFAULT_TIMEOUT):
        r = requests.post(self.base_url + path, json=json or {}, headers=self._headers(), timeout=timeout)
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
        # צ’אט מקבל timeout ארוך יותר
        return self.post("/ai/chat", {"question": question, "recipe_id": recipe_id}, timeout=60)
    # --- לוגו ---
    def get_logo_url(self, width: int = 120, height: int = 40):
        return self.get("/recipes/logo", {"width": width, "height": height})
    
    # --- הרשמה והתחברות ---
    def register(self, email: str, name: str, password: str):
        return self.post("/auth/register", {"email": email, "name": name, "password": password})

    def login(self, email: str, password: str):
        return self.post("/auth/login", {"email": email, "password": password})
    
    # --- NEW: Nutrition API Methods ---
    def get_nutrition_data(self, ingredients):
        """Get nutrition data from server API"""
        try:
            response = self.post("/nutrition/calculate", ingredients)
            if response and response.get("success"):
                return response.get("data")
            return None
        except Exception as e:
            print(f"Error getting nutrition data: {e}")
            return None

    def test_nutrition_api(self):
        """Test if nutrition API is working"""
        try:
            response = self.get("/nutrition/test")
            return response
        except Exception as e:
            print(f"Error testing nutrition API: {e}")
            return {"api_available": False, "error": str(e)}
    def get_kits(self):
             return self.get("/orders/kits")

    def place_order(self, payload: dict):
             return self.post("/orders", payload)

    def list_orders(self):
             return self.get("/orders")
