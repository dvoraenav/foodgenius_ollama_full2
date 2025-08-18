from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from presenters.auth_presenter import AuthPresenter
from components.auth_ui_builder import AuthUIBuilder

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = AuthPresenter(self)
        self.is_register_mode = False
        self.ui_builder = AuthUIBuilder()
        
        # UI Components (will be created in setup_ui)
        self.main_layout = None
        self.subtitle = None
        self.email_input = None
        self.name_input = None
        self.password_input = None
        self.login_btn = None
        self.register_btn = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('FoodGenius - כניסה למערכת')
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        
        # Create header
        header_frame, title, self.subtitle = self.ui_builder.create_header(
            'ברוכים הבאים ל-FoodGenius',
            'התחברו כדי למצוא מתכונים מותאמים אישית'
        )
        
        # Create input fields
        self.email_input = self.ui_builder.create_input_field('כתובת אימייל')
        self.name_input = self.ui_builder.create_input_field('שם מלא', is_hidden=True)
        self.password_input = self.ui_builder.create_input_field('סיסמה', is_password=True)
        
        # Create buttons
        button_layout, self.login_btn, self.register_btn = self.ui_builder.create_button_layout()
        
        # Add all to main layout
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(self.email_input)
        self.main_layout.addWidget(self.name_input)
        self.main_layout.addWidget(self.password_input)
        self.main_layout.addLayout(button_layout)
        
        # Connect signals
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.toggle_register_mode)
        self.password_input.returnPressed.connect(self.handle_action)
        
        # Set initial focus
        self.email_input.setFocus()
    
    def toggle_register_mode(self):
        """Toggle between login and register mode"""
        self.is_register_mode = not self.is_register_mode
        
        # Get appropriate texts for current mode
        texts = self.ui_builder.get_mode_texts(self.is_register_mode)
        
        # Update UI elements
        self.subtitle.setText(texts['subtitle'])
        self.login_btn.setText(texts['login_btn'])
        self.register_btn.setText(texts['register_btn'])
        
        # Show/hide name field
        if self.is_register_mode:
            self.name_input.show()
            self.name_input.setFocus()
        else:
            self.name_input.hide()
            self.name_input.clear()
            self.email_input.setFocus()
        
        # Apply button styles
        self.ui_builder.apply_button_styles(self.login_btn, self.register_btn, self.is_register_mode)
    
    def handle_action(self):
        """Handle Enter key press - login or register based on mode"""
        if self.is_register_mode:
            self.handle_register()
        else:
            self.handle_login()
        
    def handle_login(self):
        """Handle login button click"""
        if self.is_register_mode:
            # If in register mode, switch back to login
            self.toggle_register_mode()
            return
            
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not self._validate_login_fields(email, password):
            return
            
        try:
            self.presenter.login(email, password)
            self.accept()  # Close dialog and proceed to main app
        except Exception as e:
            QMessageBox.critical(self, 'שגיאת כניסה', str(e))
    
    def handle_register(self):
        """Handle registration"""
        email = self.email_input.text().strip()
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()
        
        if not self._validate_register_fields(email, name, password):
            return
            
        try:
            self.presenter.register(email, name, password)
            QMessageBox.information(self, 'הרשמה הושלמה', 
                                  'נרשמת בהצלחה! כעת המערכת תעבור למסך הכניסה.')
            # Switch back to login mode after successful registration
            self.toggle_register_mode()
            # Clear password for security
            self.password_input.clear()
        except Exception as e:
            QMessageBox.critical(self, 'שגיאת הרשמה', str(e))
    
    def _validate_login_fields(self, email: str, password: str) -> bool:
        """Validate login fields"""
        if not email or not password:
            QMessageBox.warning(self, 'שגיאה', 'נא למלא את כל השדות הנדרשים')
            return False
        return True
    
    def _validate_register_fields(self, email: str, name: str, password: str) -> bool:
        """Validate registration fields"""
        if not email or not name or not password:
            QMessageBox.warning(self, 'שגיאה', 'נא למלא את כל השדות להרשמה')
            return False
        return True