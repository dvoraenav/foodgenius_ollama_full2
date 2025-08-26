# server/api/orders.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3, os, time

router = APIRouter()

# ---- קטלוג ערכות (אפשר לעבור לדאטהבייס אח"כ) ----
KITS = [
    {
        "id": "sushi_basic",
        "title": "Sushi Starter",
        "subtitle": "כל מה שצריך ל-2 רולים",
        "price": 79,
        "image": "https://res.cloudinary.com/demo/image/upload/v1711111111/sushi.png",
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
        "image": "https://res.cloudinary.com/demo/image/upload/v1711111111/bowl.png",
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

# ---- SQLite (ללא תלות בקוד קיים) ----
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "foodgenius.db")

def _conn():
    return sqlite3.connect(DB_PATH)

def _init_db():
    with _conn() as cx:
        cx.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_email TEXT,
            kit_id TEXT NOT NULL,
            kit_title TEXT NOT NULL,
            price INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            notes TEXT
        )
        """)
_init_db()

# ---- סכימות ----
class OrderIn(BaseModel):
    kit_id: str = Field(..., examples=["sushi_basic"])
    full_name: str
    phone: str
    address: str
    notes: Optional[str] = ""

    # אופציונלי – אם יש לך מזהה משתמש/אימייל בלקוח
    user_email: Optional[str] = None

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

# ---- ראוטים ----
@router.get("/kits")
def list_kits() -> List[dict]:
    return KITS

@router.post("", response_model=OrderOut)
def create_order(order: OrderIn):
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
        oid = cur.lastrowid

    return OrderOut(
        id=oid, created_at=created_at,
        kit_id=kit["id"], kit_title=kit["title"], price=int(kit["price"]),
        full_name=order.full_name, phone=order.phone, address=order.address,
        notes=order.notes or "", user_email=order.user_email
    )

@router.get("", response_model=List[OrderOut])
def my_orders(email: Optional[str] = Query(default=None)):
    """היסטוריית הזמנות (אפשר לסנן לפי אימייל אם רוצים)"""
    q = "SELECT id, created_at, user_email, kit_id, kit_title, price, full_name, phone, address, notes FROM orders"
    args: tuple = ()

    if email:
        q += " WHERE user_email = ?"
        args = (email,)

    q += " ORDER BY id DESC"

    rows = []
    with _conn() as cx:
        for r in cx.execute(q, args):
            rows.append(OrderOut(
                id=r[0], created_at=r[1], user_email=r[2],
                kit_id=r[3], kit_title=r[4], price=r[5],
                full_name=r[6], phone=r[7], address=r[8], notes=r[9]
            ))
    return rows
