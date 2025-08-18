from PySide6.QtWidgets import QDialog, QVBoxLayout
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
        self.error_label = None
        self.success_label = None
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
        
        # Create message labels
        self.error_label = self.ui_builder.create_error_message()
        self.success_label = self.ui_builder.create_success_message()
        
        # Create input fields
        self.email_input = self.ui_builder.create_input_field('כתובת אימייל')
        self.name_input = self.ui_builder.create_input_field('שם מלא', is_hidden=True)
        self.password_input = self.ui_builder.create_input_field('סיסמה', is_password=True)
        
        # Create buttons
        button_layout, self.login_btn, self.register_btn = self.ui_builder.create_button_layout()
        
        # Add all to main layout
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(self.error_label)
        self.main_layout.addWidget(self.success_label)
        self.main_layout.addWidget(self.email_input)
        self.main_layout.addWidget(self.name_input)
        self.main_layout.addWidget(self.password_input)
        self.main_layout.addLayout(button_layout)
        
        # Connect signals
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.toggle_register_mode)
        self.password_input.returnPressed.connect(self.handle_action)
        
        # Hide messages when user starts typing
        self.email_input.textChanged.connect(self.clear_messages)
        self.name_input.textChanged.connect(self.clear_messages)
        self.password_input.textChanged.connect(self.clear_messages)
        
        # Set initial focus
        self.email_input.setFocus()
    
    def clear_messages(self):
        """Clear error and success messages"""
        self.ui_builder.hide_messages(self.error_label, self.success_label)
    
    def toggle_register_mode(self):
        """Toggle between login and register mode"""
        self.clear_messages()  # Clear messages when switching modes
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
            self.ui_builder.show_error_message(self.error_label, str(e))
    
    def handle_register(self):
        """Handle registration"""
        email = self.email_input.text().strip()
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()
        
        print(f"DEBUG: Starting registration for: {email}")
        
        if not self._validate_register_fields(email, name, password):
            print("DEBUG: Validation failed")
            return
            
        print("DEBUG: About to call presenter.register")
        try:
            result = self.presenter.register(email, name, password)
            print(f"DEBUG: Register completed successfully, result: {result}")
            
            # Only if we get here without exception, registration was successful
            self.ui_builder.show_success_message(self.success_label, 
                                               'נרשמת בהצלחה! כעת תוכל להתחבר עם הפרטים שהזנת.')
            # Switch back to login mode only after successful registration
            print("DEBUG: About to toggle to login mode")
            self.toggle_register_mode()
            # Clear password for security
            self.password_input.clear()
            print("DEBUG: Registration flow completed successfully")
            
        except Exception as e:
            print(f"DEBUG: Register exception caught: {type(e).__name__}: {str(e)}")
            # Registration failed - stay in register mode and show error
            self.ui_builder.show_error_message(self.error_label, str(e))
            print("DEBUG: Staying in register mode due to error")
            # Don't switch modes on error
    
    def _validate_login_fields(self, email: str, password: str) -> bool:
        """Validate login fields"""
        if not email or not password:
            self.ui_builder.show_error_message(self.error_label, 'נא למלא את כל השדות הנדרשים')
            return False
        return True
    
    def _validate_register_fields(self, email: str, name: str, password: str) -> bool:
        """Validate registration fields"""
        if not email or not name or not password:
            self.ui_builder.show_error_message(self.error_label, 'נא למלא את כל השדות להרשמה')
            return False
        return True