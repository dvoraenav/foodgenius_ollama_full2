import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# -------------------------------
# הגדרת מסד הנתונים
# -------------------------------

# כתובת מסד הנתונים – אם קיים משתנה סביבה DB_URL, נשתמש בו
# אחרת נשתמש ב-SQLite מקומי בשם foodgenius.db
DB_URL = os.getenv("DB_URL", "sqlite:///./foodgenius.db")

# יצירת engine (חיבור למסד הנתונים)
# עבור SQLite נדרשת connect_args כדי לא לאפשר בעיות חיבור עם threads
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
)

# יצירת מחלקת session לעבודה מול מסד הנתונים
# session מאפשרת לבצע שאילתות והוספות
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# מחלקת בסיס לכל הטבלאות ב-ORM
Base = declarative_base()

# -------------------------------
# מודל משתמש
# -------------------------------

class User(Base):
    """
    מודל המשתמשים במסד הנתונים
    כל אובייקט User מייצג שורה בטבלת 'users'
    """
    __tablename__ = "users"  # שם הטבלה במסד

    id = Column(Integer, primary_key=True, index=True)
    # מזהה ייחודי לכל משתמש (מספרי, עוקב)

    email = Column(String, unique=True, index=True, nullable=False)
    # כתובת דוא"ל של המשתמש, חייבת להיות ייחודית

    password_hash = Column(String, nullable=False)
    # כאן נשמר ה-Hash של הסיסמה
    # לא נשמרת הסיסמה גולמית אלא בצורה מוצפנת/מוטמעת (hash)
    # זה כדי לאחסן סיסמאות בצורה מאובטחת

    name = Column(String, nullable=False)
    # שם מלא של המשתמש

    created_at = Column(DateTime, default=datetime.utcnow)
    # תאריך יצירת המשתמש, נשמר אוטומטית

# -------------------------------
# פונקציה ליצירת טבלאות
# -------------------------------

def init_db():
    """
    יוצרת את כל הטבלאות שהוגדרו ב-Base אם הן עדיין לא קיימות
    - חשוב להריץ פעם אחת בתחילת הפרויקט
    """
    Base.metadata.create_all(engine)
