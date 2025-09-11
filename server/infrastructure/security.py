from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt, os

# -------- הגדרות הצפנה וסיסמאות --------
# pwd – אובייקט לטיפול בהצפנת סיסמאות ובדיקתן
# אנחנו משתמשים ב-bcrypt, שהוא סטנדרט בטוח להצפנת סיסמאות
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# מפתח סודי ליצירת JWT – אם לא מוגדר במשתני סביבה, מוגדר ברירת מחדל
JWT_SECRET = os.getenv("JWT_SECRET", "change_me")

# אלגוריתם החתימה של ה-JWT
JWT_ALG = "HS256"

# -------- פונקציות סיסמאות --------
def hash_password(p: str) -> str:
    """
    מקבל סיסמה כטקסט רגיל ומחזיר גרסת hash מוצפנת
    שנשמרת בבסיס הנתונים.
    """
    return pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    """
    בודק אם סיסמה רגילה (p) תואמת ל-hash השמור (h).
    מחזיר True אם הסיסמא נכונה.
    """
    return pwd.verify(p, h)

# -------- פונקציות JWT (JSON Web Token) --------
def create_token(sub: str, minutes: int = 60*24) -> str:
    """
    יוצר token JWT עם:
    - sub: מזהה המשתמש (למשל email או id)
    - exp: זמן תפוגה (ברירת מחדל: 24 שעות)
    מחזיר מחרוזת token חתומה.
    """
    payload = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=minutes)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> dict:
    """
    מקבל token JWT ומחזיר את ה-payload (כולל sub ו-exp)
    אם החתימה תקינה. יגרום לשגיאה אם החתימה לא תואמת או התוקף פג.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
