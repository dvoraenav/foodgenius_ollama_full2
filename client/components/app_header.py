from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
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

class AppHeader(QFrame):
    def __init__(self, on_logout, user=None):
        super().__init__()
        self.setObjectName('Header')
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # לוגו
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(120, 40)
        self.logo_label.setScaledContents(False)  # שונה מ-True ל-False
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet('''
            QLabel {
                background: rgba(255,255,255,0.1);
                border-radius: 5px;
                padding: 5px;
            }
        ''')
        
        # טוען את הלוגו מהשרת
        self.load_logo()
        
        # Title
        title = QLabel('FoodGenius — מצאי מתכונים לפי חומרים')
        title.setStyleSheet('font-weight:700; color:white; font-size:16px;')
        
        # User info and logout button
        if user:
            # Welcome message
            welcome_label = QLabel(f'שלום {user.get("name", user.get("email", ""))}!')
            welcome_label.setStyleSheet('color:white; font-size:14px;')
            
            # Logout button with visible border/frame
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
            
            # סידור הרכיבים
            layout.addWidget(self.logo_label)
            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(welcome_label)
            layout.addWidget(logout_btn)
        else:
            # Fallback for when no user is provided
            login_btn = QPushButton('כניסה / הרשמה')
            login_btn.setProperty('accent', True)
            login_btn.clicked.connect(on_logout)  # This would be on_login in original
            
            layout.addWidget(self.logo_label)
            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(login_btn)
    
    def load_logo(self):
        """טוען את הלוגו מהשרת"""
        try:
            api_client = ApiClient()
            response = api_client.get_logo_url(width=120, height=40)
            
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
        # התאם את הגודל תוך שמירה על יחס גובה-רוחב
        scaled_pixmap = pixmap.scaled(
            110, 30,  # גודל קטן יותר כדי להשאיר מקום לרווח
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.logo_label.setPixmap(scaled_pixmap)
    
    def set_fallback_logo(self):
        """מציג טקסט במקום לוגו אם יש בעיה"""
        self.logo_label.setText("🍽️")
        self.logo_label.setStyleSheet('''
            font-size: 24px;
            color: white;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        ''')