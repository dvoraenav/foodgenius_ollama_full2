import requests
from config import API_BASE_URL
from services.auth import AUTH

DEFAULT_TIMEOUT = 60

class ApiClient:
    """
    ממשק אחיד לכל הקריאות לשרת
    ApiClient אחראי על ביצוע קריאות HTTP לשרת עבור כל הפעולות במערכת:
    - Authentication (הרשמה, כניסה)
    - הזמנות (Orders)
    - קבלת מתכונים חיצוניים
    - AI Chat
    - לוגו
    כל הקריאות מבוצעות עם headers מתאימים (כולל Authorization אם המשתמש מחובר).
    """

    def __init__(self, base_url: str = API_BASE_URL):
        """
        אתחול ApiClient עם כתובת בסיסית ל-API.

        :param base_url: כתובת בסיסית של ה-API (ברירת מחדל: API_BASE_URL)
        """
        self.base_url = base_url.rstrip("/")

    def _headers(self):
        """
        מחזיר את ה-Headers הדרושים לקריאות HTTP.
        אם המשתמש מחובר (AUTH.token קיים), מוסיף Authorization Bearer.

        :return: dict עם headers
        """
        headers = {"Content-Type": "application/json"}
        if AUTH.token:
            headers["Authorization"] = f"Bearer {AUTH.token}"
        return headers

    def get(self, path: str, params=None, timeout: int = DEFAULT_TIMEOUT):
        """
        מבצע קריאת GET לשרת.

        :param path: הנתיב ל-API
        :param params: פרמטרי URL (query params)
        :param timeout: זמן מקסימלי להמתנה (בשניות)
        :return: JSON של התגובה מהשרת
        :raises: Exception אם השרת מחזיר סטטוס שגיאה
        """
        r = requests.get(self.base_url + path, params=params, headers=self._headers(), timeout=timeout)
        if not r.ok:
            raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    def post(self, path: str, json=None, timeout: int = DEFAULT_TIMEOUT):
        """
        מבצע קריאת POST לשרת עם נתונים.

        :param path: הנתיב ל-API
        :param json: תוכן גוף הבקשה
        :param timeout: זמן מקסימלי להמתנה (בשניות)
        :return: JSON של התגובה מהשרת
        :raises: Exception אם השרת מחזיר סטטוס שגיאה
        """
        r = requests.post(self.base_url + path, json=json or {}, headers=self._headers(), timeout=timeout)
        if not r.ok:
            raise Exception(f"{r.status_code}: {r.text}")
        return r.json()

    # --- מתכונים חיצוניים (TheMealDB) ---
    def get_external_recipes(self, query: str):
        """
        מחפש מתכונים חיצוניים לפי מחרוזת חיפוש.

        :param query: מונח חיפוש (למשל "pasta")
        :return: רשימת מתכונים חיצוניים
        """
        return self.get("/recipes/external", {"q": query})

    def get_external_recipe_by_id(self, recipe_id: str):
        """
        מקבל פרטי מתכון חיצוני לפי מזהה.

        :param recipe_id: מזהה המתכון בשרת חיצוני
        :return: פרטי המתכון
        """
        return self.get(f"/recipes/external/{recipe_id}")

    # --- AI Chat ---
    def chat(self, question: str, recipe_id: str | None = None):
        """
        שולח שאלה ל-AI Chat, עם אפשרות לציין מתכון.

        :param question: השאלה למערכת ה-AI
        :param recipe_id: מזהה מתכון רלוונטי (אופציונלי)
        :return: תשובה מה-AI
        """
        # צ’אט מקבל timeout ארוך יותר
        return self.post("/ai/chat", {"question": question, "recipe_id": recipe_id}, timeout=60)

    # --- לוגו ---
    def get_logo_url(self, width: int = 120, height: int = 40):
        """
        מקבל URL ללוגו המותאם למידות נתונות.

        :param width: רוחב הלוגו
        :param height: גובה הלוגו
        :return: URL ללוגו
        """
        return self.get("/recipes/logo", {"width": width, "height": height})
    
    # --- הרשמה והתחברות ---
    def register(self, email: str, name: str, password: str):
        """
        מבצע הרשמה למערכת.

        :param email: כתובת מייל
        :param name: שם המשתמש
        :param password: סיסמה
        :return: JSON עם פרטי המשתמש או שגיאה
        """
        return self.post("/auth/register", {"email": email, "name": name, "password": password})

    def login(self, email: str, password: str):
        """
        מבצע כניסה למערכת.

        :param email: כתובת מייל
        :param password: סיסמה
        :return: JSON עם פרטי המשתמש ו-AccessToken
        """
        return self.post("/auth/login", {"email": email, "password": password})
    
    # --- הזמנות (Orders) ---
    def get_kits(self):
        """
        מחזיר את רשימת הערכות (kits) הזמינות להזמנה.

        :return: רשימת kits
        """
        return self.get("/orders/kits")

    def place_order(self, payload: dict):
        """
        מבצע הזמנה חדשה עם פרטי ההזמנה.

        :param payload: dict עם פרטי ההזמנה (כמו מזהי ערכות, כתובת וכו')
        :return: JSON עם פרטי ההזמנה שנוצרה
        """
        return self.post("/orders", payload)

    def list_orders(self):
        """
        מחזיר את רשימת ההזמנות של המשתמש.

        :return: רשימת הזמנות
        """
        return self.get("/orders")
    