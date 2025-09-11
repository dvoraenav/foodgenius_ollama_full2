from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
import requests

"""
רכיב הכותרת העליונה של האפליקציה.

מציג את שם האפליקציה, שם המשתמש המחובר (אם יש), וכפתור התנתקות או כניסה.
"""

class AppHeader(QFrame):
    def __init__(self, on_logout, user=None):
        """
        יוצר את כותרת האפליקציה הגרפית.

        :param on_logout: פונקציה שתתבצע כשלוחצים על כפתור התנתקות / כניסה.
        :param user: אובייקט שמייצג את המשתמש המחובר (אם קיים).
        """
        super().__init__()
        self.setObjectName('Header')

        # יצירת פריסת layout אופקית
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # יצירת תווית כותרת עם שם האפליקציה
        title = QLabel('FoodGenius — מצאו מתכונים לפי חומרים')
        title.setStyleSheet('font-weight:700; color:white; font-size:16px;')

        # אם המשתמש מחובר:
        if user:
            # יצירת תווית "שלום משתמש"
            welcome_label = QLabel(f'שלום {user.get("name", user.get("email", ""))}!')
            welcome_label.setStyleSheet('color:white; font-size:14px;')

            # יצירת כפתור התנתקות
            logout_btn = QPushButton('התנתקות')
            logout_btn.setProperty('accent', True)
            logout_btn.setStyleSheet('''
                QPushButton {
                    border: 2px solid white;
                    border-radius: 5px;
                    padding: 5px 15px;
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            ''')
            logout_btn.clicked.connect(on_logout)

            # הוספת רכיבים לפריסה
            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(welcome_label)
            layout.addWidget(logout_btn)
        else:
            # אם אין משתמש מחובר – יצירת כפתור כניסה/הרשמה
            login_btn = QPushButton('כניסה / הרשמה')
            login_btn.setProperty('accent', True)
            login_btn.clicked.connect(on_logout)  # שגיאה סמנטית – אמור להיות on_login

            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(login_btn)
