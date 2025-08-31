from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
import requests


# class ImageLoader(QThread):
#     """טוען תמונות ברקע"""
#     image_loaded = Signal(QPixmap)
    
#     def __init__(self, url: str):
#         super().__init__()
#         self.url = url
    
#     def run(self):
#         try:
#             response = requests.get(self.url, timeout=10)
#             if response.status_code == 200:
#                 pixmap = QPixmap()
#                 pixmap.loadFromData(response.content)
#                 if not pixmap.isNull():
#                     self.image_loaded.emit(pixmap)
#         except Exception as e:
#             print(f"שגיאה בטעינת תמונה: {e}")

class AppHeader(QFrame):
    def __init__(self, on_logout, user=None):
        super().__init__()
        self.setObjectName('Header')
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        
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
            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(welcome_label)
            layout.addWidget(logout_btn)
        else:
            # Fallback for when no user is provided
            login_btn = QPushButton('כניסה / הרשמה')
            login_btn.setProperty('accent', True)
            login_btn.clicked.connect(on_logout)  # This would be on_login in original
            
            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(login_btn)
    
    