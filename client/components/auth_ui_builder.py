from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt
import json
import re

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
    def create_error_message():
        """Create error message label"""
        error_label = QLabel()
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet('''
            QLabel {
                background-color: #ffebee;
                color: #c62828;
                border: 1px solid #ef5350;
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
                font-weight: bold;
            }
        ''')
        error_label.hide()  # Hidden by default
        return error_label
    
    @staticmethod
    def create_success_message():
        """Create success message label"""
        success_label = QLabel()
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet('''
            QLabel {
                background-color: #e8f5e8;
                color: #2e7d32;
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
                font-weight: bold;
            }
        ''')
        success_label.hide()  # Hidden by default
        return success_label
    
    @staticmethod
    def parse_error_message(error_str: str) -> str:
        """Parse and convert error message to user-friendly Hebrew"""
        # Common error patterns and their Hebrew translations
        error_patterns = {
            "Bad credentials": "פרטי התחברות שגויים",
            "Email already registered": "כתובת האימייל כבר רשומה במערכת",
            "Invalid email": "כתובת אימייל לא תקינה",
            "Password too short": "הסיסמה קצרה מדי",
            "Connection error": "שגיאת חיבור לשרת",
            "Timeout": "החיבור לשרת נכשל - נסה שוב",
            "Network error": "בעיית רשת - בדוק את החיבור שלך",
            "401": "פרטי התחברות שגויים",
            "400": "בקשה שגויה - בדוק את הפרטים שהזנת",
            "422": "פרטים לא תקינים - נסה שוב",
            "500": "שגיאה בשרת - נסה שוב מאוחר יותר",
            "404": "השירות אינו זמין כרגע"
        }
        
        # Try to extract JSON error detail
        try:
            # Look for JSON in the error string
            json_match = re.search(r'{.*}', error_str)
            if json_match:
                error_json = json.loads(json_match.group())
                if 'detail' in error_json:
                    detail = error_json['detail']
                    # Check for specific patterns first
                    if "Email already registered" in detail:
                        return "כתובת האימייל הזו כבר רשומה במערכת"
                    elif "Bad credentials" in detail:
                        return "פרטי התחברות שגויים"
                    # Check for other patterns
                    for pattern, hebrew in error_patterns.items():
                        if pattern.lower() in detail.lower():
                            return hebrew
                    return f"שגיאה: {detail}"
        except:
            pass
        
        # Check for specific error patterns in the raw string
        error_lower = error_str.lower()
        for pattern, hebrew in error_patterns.items():
            if pattern.lower() in error_lower:
                return hebrew
        
        # Extract status code if present
        status_match = re.search(r'(\d{3}):', error_str)
        if status_match:
            status_code = status_match.group(1)
            if status_code in error_patterns:
                return error_patterns[status_code]
            return f"שגיאה {status_code} - נסה שוב מאוחר יותר"
        
        # Check for specific 422 validation errors
        if "422" in error_str:
            if "email" in error_lower:
                return "כתובת האימייל לא תקינה"
            elif "password" in error_lower:
                return "הסיסמה לא עומדת בדרישות"
            elif "name" in error_lower:
                return "השם לא תקין"
            else:
                return "הפרטים שהוזנו לא תקינים - בדוק ונסה שוב"
        
        # Default fallback
        return "שגיאה לא צפויה - נסה שוב מאוחר יותר"
    
    @staticmethod
    def show_error_message(error_label: QLabel, message: str):
        """Show error message with exclamation icon"""
        # Parse the error message to make it user-friendly
        friendly_message = AuthUIBuilder.parse_error_message(message)
        error_label.setText(f"⚠️ {friendly_message}")
        error_label.show()
    
    @staticmethod
    def show_success_message(success_label: QLabel, message: str):
        """Show success message with check icon"""
        success_label.setText(f"✅ {message}")
        success_label.show()
    
    @staticmethod
    def hide_messages(error_label: QLabel, success_label: QLabel):
        """Hide both error and success messages"""
        error_label.hide()
        success_label.hide()
    
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