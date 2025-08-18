from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QPushButton, QMessageBox, QLabel, QFrame)
from PySide6.QtCore import Qt
from presenters.auth_presenter import AuthPresenter

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = AuthPresenter(self)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('FoodGenius - כניסה למערכת')
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Welcome header
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        welcome_title = QLabel('ברוכים הבאים ל-FoodGenius')
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;')
        
        subtitle = QLabel('מצאו מתכונים מותאמים אישית לחומרים שלכם')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('font-size: 14px; color: #7f8c8d; margin-bottom: 20px;')
        
        header_layout.addWidget(welcome_title)
        header_layout.addWidget(subtitle)
        
        # Input fields
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('כתובת אימייל')
        self.email_input.setMinimumHeight(35)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('שם מלא (להרשמה בלבד)')
        self.name_input.setMinimumHeight(35)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('סיסמה')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton('כניסה')
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setProperty('accent', True)
        
        self.register_btn = QPushButton('הרשמה')
        self.register_btn.setMinimumHeight(40)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        
        # Add all to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(self.email_input)
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(self.password_input)
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.handle_register)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Set initial focus
        self.email_input.setFocus()
        
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, 'שגיאה', 'נא למלא את כל השדות הנדרשים')
            return
            
        try:
            self.presenter.login(email, password)
            self.accept()  # Close dialog and proceed to main app
        except Exception as e:
            QMessageBox.critical(self, 'שגיאת כניסה', str(e))
    
    def handle_register(self):
        email = self.email_input.text().strip()
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not name or not password:
            QMessageBox.warning(self, 'שגיאה', 'נא למלא את כל השדות להרשמה')
            return
            
        try:
            self.presenter.register(email, name, password)
            QMessageBox.information(self, 'הרשמה הושלמה', 
                                  'נרשמת בהצלחה! כעת תוכל להתחבר עם הפרטים שהזנת.')
            # Clear name field after successful registration
            self.name_input.clear()
        except Exception as e:
            QMessageBox.critical(self, 'שגיאת הרשמה', str(e))