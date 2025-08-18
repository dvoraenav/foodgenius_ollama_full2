from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt

class AuthUIBuilder:
    """Helper class to build authentication UI components"""
    
    @staticmethod
    def create_header(title_text: str, subtitle_text: str):
        """Create header with title and subtitle"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;')
        
        subtitle = QLabel(subtitle_text)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('font-size: 14px; color: #7f8c8d; margin-bottom: 20px;')
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        return header_frame, title, subtitle
    
    @staticmethod
    def create_input_field(placeholder: str, is_password: bool = False, is_hidden: bool = False):
        """Create styled input field"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setMinimumHeight(35)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        
        if is_hidden:
            input_field.hide()
            
        return input_field
    
    @staticmethod
    def create_button_layout():
        """Create button layout with two buttons"""
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton('כניסה')
        login_btn.setMinimumHeight(40)
        login_btn.setProperty('accent', True)
        
        register_btn = QPushButton('הרשמה')
        register_btn.setMinimumHeight(40)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        
        return button_layout, login_btn, register_btn
    
    @staticmethod
    def apply_button_styles(login_btn: QPushButton, register_btn: QPushButton, is_register_mode: bool):
        """Apply appropriate styles to buttons based on mode"""
        if is_register_mode:
            # Register mode - register button green, login button white
            register_btn.setProperty('accent', True)
            login_btn.setProperty('accent', False)
            register_btn.setStyleSheet('')  # Reset to default accent style
            login_btn.setStyleSheet('background-color: white; color: #2c3e50; border: 1px solid #bdc3c7;')
        else:
            # Login mode - login button green, register button white
            login_btn.setProperty('accent', True)
            register_btn.setProperty('accent', False)
            login_btn.setStyleSheet('')  # Reset to default accent style
            register_btn.setStyleSheet('background-color: white; color: #2c3e50; border: 1px solid #bdc3c7;')
        
        # Force style refresh
        AuthUIBuilder.refresh_button_style(login_btn)
        AuthUIBuilder.refresh_button_style(register_btn)
    
    @staticmethod
    def refresh_button_style(button: QPushButton):
        """Force refresh button style"""
        button.style().unpolish(button)
        button.style().polish(button)
    
    @staticmethod
    def get_mode_texts(is_register_mode: bool):
        """Get appropriate texts for current mode"""
        if is_register_mode:
            return {
                'subtitle': 'הרשמו כדי ליצור חשבון חדש במערכת',
                'login_btn': 'חזור לכניסה',
                'register_btn': 'אישור הרשמה'
            }
        else:
            return {
                'subtitle': 'התחברו כדי למצוא מתכונים מותאמים אישית',
                'login_btn': 'כניסה',
                'register_btn': 'הרשמה'
            }