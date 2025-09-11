from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3, os, time

router = APIRouter()

# -------- רשימת ערכות (kits) זמינות להזמנה --------
KITS = [
    {
        "id": "sushi_basic",
        "title": "Sushi Starter",
        "subtitle": "כל מה שצריך ל-2 רולים",
        "price": 79,
        "image": "https://tse3.mm.bing.net/th/id/OIP.-aNnJc0ncLaGmSF2_WJCCQHaE7?rs=1&pid=ImgDetMain&o=7&rm=3",
        "items": ["אורז סושי", "אצות נורי", "חומץ אורז", "סוכר", "מלח", "מחצלת גלגול"]
    },
    {
        "id": "pizza_family",
        "title": "Family Pizza",
        "subtitle": "3 בצקים, רוטב, גבינה ותוספות",
        "price": 89,
        "image": "https://res.cloudinary.com/demo/image/upload/v1711111111/pizza.png",
        "items": ["קמח פיצה", "שמרים", "רוטב עגבניות", "גבינה", "זיתים", "תירס"]
    },
    {
        "id": "vegan_bowl",
        "title": "Vegan Bowl",
        "subtitle": "קערות בריאות ל-2",
        "price": 69,
        "image": "https://www.sarayanews.com/image.php?token=499bbfa273d439a28eba3a39df45a234&size=",
        "items": ["קינואה", "חומוס מבושל", "אבוקדו", "ירקות שורש", "טחינה"]
    },
    {
        "id": "cookies_fun",
        "title": "Cookies Fun",
        "subtitle": "ערכת עוגיות צבעונית",
        "price": 59,
        "image": "https://res.cloudinary.com/demo/image/upload/v1711111111/cookies.png",
        "items": ["קמח", "סוכר", "חמאה", "שוקולד צ'יפס", "סוכריות לקישוט"]
    },
]

# -------- נתיב לבסיס הנתונים SQLite --------
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "foodgenius.db")

# פונקציה לפתיחת חיבור לבסיס הנתונים
def _conn():
    return sqlite3.connect(DB_PATH)

# יצירת טבלת ההזמנות אם אינה קיימת
def _init_db():
    with _conn() as cx:
        cx.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       -- מזהה ייחודי להזמנה
            created_at TEXT NOT NULL,                   -- תאריך יצירת ההזמנה
            user_email TEXT,                            -- דוא"ל המשתמש שביצע את ההזמנה
            kit_id TEXT NOT NULL,                       -- מזהה הערכה שהוזמנה
            kit_title TEXT NOT NULL,                    -- שם הערכה
            price INTEGER NOT NULL,                     -- מחיר
            full_name TEXT NOT NULL,                    -- שם מלא של המזמין
            phone TEXT NOT NULL,                        -- טלפון
            address TEXT NOT NULL,                      -- כתובת
            notes TEXT                                  -- הערות נוספות
        )
        """)
# קריאה ליצירת הטבלה במידת הצורך
_init_db()

# -------- מודלים של Pydantic --------
class OrderIn(BaseModel):
    kit_id: str = Field(..., examples=["sushi_basic"])  # מזהה הערכה
    full_name: str                                      # שם המזמין
    phone: str                                         # טלפון
    address: str                                       # כתובת
    notes: Optional[str] = ""                          # הערות נוספות (אופציונלי)
    user_email: Optional[str] = None                   # דוא"ל המזמין (אופציונלי)

class OrderOut(BaseModel):
    id: int
    created_at: str
    kit_id: str
    kit_title: str
    price: int
    full_name: str
    phone: str
    address: str
    notes: Optional[str] = ""
    user_email: Optional[str] = None

# -------- מסלולי API --------
@router.get("/kits")
def list_kits() -> List[dict]:
    """
    מחזיר את כל הערכות הזמינות להזמנה
    """
    return KITS

@router.post("", response_model=OrderOut)
def create_order(order: OrderIn):
    """
    יוצר הזמנה חדשה:
    1. בודק שה-kit_id קיים ברשימת הערכות
    2. יוצר רשומה חדשה בטבלת orders
    3. מחזיר את פרטי ההזמנה שיצרנו
    """
    kit = next((k for k in KITS if k["id"] == order.kit_id), None)
    if not kit:
        raise HTTPException(status_code=400, detail="Unknown kit_id")

    created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as cx:
        cur = cx.execute("""
            INSERT INTO orders (created_at, user_email, kit_id, kit_title, price,
                                full_name, phone, address, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at,
            order.user_email,
            kit["id"], kit["title"], int(kit["price"]),
            order.full_name, order.phone, order.address, order.notes or ""
        ))
        oid = cur.lastrowid  # מזהה ההזמנה החדש

    return OrderOut(
        id=oid, created_at=created_at,
        kit_id=kit["id"], kit_title=kit["title"], price=int(kit["price"]),
        full_name=order.full_name, phone=order.phone, address=order.address,
        notes=order.notes or "", user_email=order.user_email
    )

