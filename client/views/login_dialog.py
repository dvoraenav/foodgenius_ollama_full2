from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt

from presenters.auth_presenter import AuthPresenter
from components.auth_ui_builder import AuthUIBuilder

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("התחברות")
        self.setMinimumWidth(400)

        self.presenter = AuthPresenter(self)
        self.ui = AuthUIBuilder()
        self.is_register_mode = False

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.error_label)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("כתובת מייל")
        self.layout.addWidget(self.email_input)

        # Name input (רק בהרשמה)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("שם מלא")
        self.layout.addWidget(self.name_input)

        # Password input
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("סיסמה")
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.pw_input)

        # Toggle button
        self.toggle_button = QPushButton("אין לך חשבון? הרשם כאן")
        self.toggle_button.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.toggle_button)

        # Submit button
        self.submit_button = QPushButton("התחברות")
        self.submit_button.clicked.connect(self.handle_submit)
        self.layout.addWidget(self.submit_button)

        # מצב התחלתי – התחברות
        self.name_input.hide()

        self.apply_styles()

    def apply_styles(self):
        style = """
        QLineEdit {
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1abc9c, stop:1 #16a085);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #148f77;
        }
        QLabel {
            font-size: 13px;
        }
        """
        self.setStyleSheet(style)


    def toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        if self.is_register_mode:
            self.setWindowTitle("הרשמה")
            self.submit_button.setText("הרשמה")
            self.toggle_button.setText("כבר יש לך חשבון? לחץ כאן להתחברות")
            self.name_input.show()
        else:
            self.setWindowTitle("התחברות")
            self.submit_button.setText("התחברות")
            self.toggle_button.setText("אין לך חשבון? הרשם כאן")
            self.name_input.hide()
        self.ui.clear_messages(self.error_label)

    def handle_submit(self):
        email = self.email_input.text().strip()
        name = self.name_input.text().strip()
        pw = self.pw_input.text().strip()

        self.ui.clear_messages(self.error_label)

        if self.is_register_mode:
            if not self._validate_email(email):
                return
            if not name:
                self.ui.show_error_message(self.error_label, "יש להזין שם מלא")
                return
            if len(pw) < 6:
                self.ui.show_error_message(self.error_label, "סיסמה חייבת להכיל לפחות 6 תווים")
                return

            success, message = self.presenter.register(email, name, pw)
            if success:
                self.ui.show_success_message(self.error_label, "נרשמת בהצלחה! כעת התחבר/י.")
                self.toggle_mode()  # רק אם הצליח עוברים להתחברות
            else:
                self.ui.show_error_message(self.error_label, message)

        else:  # login
            if not email or not pw:
                self.ui.show_error_message(self.error_label, "נא למלא את כל השדות")
                return

            success, message = self.presenter.login(email, pw)
            if success:
                self.accept()
            else:
                self.ui.show_error_message(self.error_label, message)

    def _validate_email(self, email: str) -> bool:
        if not email:
            self.ui.show_error_message(self.error_label, "יש להזין כתובת מייל")
            return False
        if '@' not in email or '.' not in email:
            self.ui.show_error_message(self.error_label, "כתובת מייל לא תקינה – חייבת לכלול @ ו־.")
            return False
        return True
