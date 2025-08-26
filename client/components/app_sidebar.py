# client/components/app_sidebar.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Signal, Qt

class AppSidebar(QFrame):
    # מפתחות ניווט: 'recipes' | 'orders' | 'chatbot'
    navigate = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(170)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 12, 10, 12)
        lay.setSpacing(8)

        # כפתורי הניווט
        self.btn_recipes = self._make_btn("🍽️  Recipes",  "recipes")
        self.btn_orders  = self._make_btn("🧺  Orders",   "orders")
        self.btn_chat    = self._make_btn("🤖  ChatBot",  "chatbot")

        for b in (self.btn_recipes, self.btn_orders, self.btn_chat):
            lay.addWidget(b)

        lay.addStretch(1)

        # סטייל בסיסי
        self.setStyleSheet("""
            #Sidebar { background: #ffffff; border-right: 1px solid #e5e7eb; }
            QPushButton {
                text-align: left;
                padding: 10px 12px;
                border: 0;
                border-radius: 10px;
                background: #f3f4f6;
                font-weight: 600;
            }
            QPushButton:hover { background: #e5e7eb; }
            QPushButton[active="true"] { background: #10b981; color: white; }
        """)

        # ברירת מחדל – מסמן "Recipes" כפעיל
        self.set_active("recipes")

    def _make_btn(self, text: str, key: str) -> QPushButton:
        b = QPushButton(text)
        b.setProperty("navkey", key)
        b.setCursor(Qt.PointingHandCursor)
        b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        b.clicked.connect(lambda: self.navigate.emit(key))
        return b

    def set_active(self, key: str):
        """מסמן כפתור פעיל לפי מפתח הניווט ומרענן את ה־style."""
        for b in (self.btn_recipes, self.btn_orders, self.btn_chat):
            b.setProperty("active", b.property("navkey") == key)
            b.style().unpolish(b); b.style().polish(b)
