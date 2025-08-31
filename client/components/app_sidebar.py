# client/components/app_sidebar.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QSizePolicy, QLabel
from PySide6.QtCore import Signal, Qt, QThread
from PySide6.QtGui import QPixmap
import requests
from services.api_client import ApiClient

class ImageLoader(QThread):
    """טוען תמונות ברקע"""
    image_loaded = Signal(QPixmap)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                if not pixmap.isNull():
                    self.image_loaded.emit(pixmap)
        except Exception as e:
            print(f"שגיאה בטעינת תמונה: {e}") 

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

        # לוגו בתחתית
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(180, 140)  
        self.logo_label.setScaledContents(False)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet('''
            QLabel {
                background: transparent;
                border: none;
                padding: 5px;
                margin: 10px 0px;
            }
        ''')

        # טוען את הלוגו מהשרת
        self.load_logo()

        lay.addStretch(1)
        lay.addWidget(self.logo_label)

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
   
    def load_logo(self):
        """טוען את הלוגו מהשרת"""
        try:
            api_client = ApiClient()
            response = api_client.get_logo_url(width=180, height=140)
            
            if response.get("status") == "success" and response.get("logo_url"):
                # טוען את התמונה ברקע
                self.image_loader = ImageLoader(response["logo_url"])
                self.image_loader.image_loaded.connect(self.on_logo_loaded)
                self.image_loader.start()
            else:
                print(f"שגיאה בקבלת URL הלוגו: {response}")
                self.set_fallback_logo()
                
        except Exception as e:
            print(f"שגיאה בטעינת לוגו: {e}")
            self.set_fallback_logo()

    def on_logo_loaded(self, pixmap: QPixmap):
        """נקרא כשהתמונה נטענת בהצלחה"""
        
        scaled_pixmap = pixmap.scaled(
            150, 110,  
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.logo_label.setPixmap(scaled_pixmap)

    def set_fallback_logo(self):
        """מציג טקסט במקום לוגו אם יש בעיה"""
        self.logo_label.setText("FoodGenius")
        self.logo_label.setStyleSheet('''
            font-size: 16px;
            font-weight: bold;
            color: #10b981;
            background: transparent;
            border: none;
            padding: 5px;
        ''')