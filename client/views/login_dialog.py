from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import requests

from presenters.auth_presenter import AuthPresenter
from components.auth_ui_builder import AuthUIBuilder


HERO_URL = "https://gilacooking.co.il/wp-content/uploads/pineapple-smoothie-recipe.jpeg"


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("התחברות")
        # חלון גדול שאפשר להגדיל
        self.setMinimumSize(900, 620)

        self.presenter = AuthPresenter(self)
        self.ui = AuthUIBuilder()
        self.is_register_mode = False

        self._hero_pix = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        # ---------------- HERO (תמונה + טקסט) ----------------
        self.hero = QFrame()
        self.hero.setObjectName("Hero")
        self.hero.setFixedHeight(320)  # אפשר להעלות ל-360 אם רוצים עוד גובה
        self.hero.setStyleSheet('QFrame#Hero { border-radius: 14px; background: #0f172a; }')

        # שכבת תמונה
        self.hero_img = QLabel(self.hero)
        self.hero_img.setGeometry(0, 0, self.hero.width(), self.hero.height())
        self.hero_img.setScaledContents(False)

        # שכבת גרדיאנט + טקסט
        self.hero_overlay = QWidget(self.hero)
        self.hero_overlay.setGeometry(0, 0, self.hero.width(), self.hero.height())
        self.hero_overlay.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0, x2:0,y2:1,
                                        stop:0 rgba(0,0,0,0.45),
                                        stop:1 rgba(0,0,0,0.18));
            border-radius: 14px;
        """)
        ov = QVBoxLayout(self.hero_overlay)
        ov.setContentsMargins(20, 20, 20, 20)
        ov.addStretch(1)

        t1 = QLabel("Welcome to FoodGenius", self.hero_overlay)
        t1.setAlignment(Qt.AlignCenter)
        t1.setStyleSheet("color:#ffffff; font-size:26px; font-weight:800;")
        ov.addWidget(t1)

        t2 = QLabel("הדרך שלך להתאהב במטבח", self.hero_overlay)
        t2.setAlignment(Qt.AlignCenter)
        t2.setStyleSheet("color:#e5e7eb; font-size:14px;")
        ov.addWidget(t2)

        ov.addStretch(2)

        # התאמת כיסוי התמונה בכל שינוי גודל
        def _hero_resized(e):
            self.hero_img.setGeometry(0, 0, self.hero.width(), self.hero.height())
            self.hero_overlay.setGeometry(0, 0, self.hero.width(), self.hero.height())
            self._apply_hero_cover()
            QFrame.resizeEvent(self.hero, e)
        self.hero.resizeEvent = _hero_resized

        self.layout.addWidget(self.hero)
        self._load_hero()
        # ---------------- /HERO ----------------

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

    def _load_hero(self):
        """טוען את תמונת ה-hero מה-URL שנתת."""
        try:
            r = requests.get(HERO_URL, timeout=10)
            if r.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(r.content)
                if not pix.isNull():
                    self._hero_pix = pix
                    self._apply_hero_cover()
        except Exception:
            # במקרה של כשל — פשוט נשאר רקע כהה, בלי שגיאה למשתמש
            pass

    def _apply_hero_cover(self):
        """מציג את התמונה במצב cover (ממלא עם חיתוך עדין)."""
        if not self._hero_pix:
            return
        W = max(1, self.hero_img.width())
        H = max(1, self.hero_img.height())
        cover = self._hero_pix.scaled(W, H, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.hero_img.setPixmap(cover)

    def apply_styles(self):
        style = """
        QDialog { background: #ffffff; }
        QLineEdit {
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1abc9c, stop:1 #16a085);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton:hover { background-color: #148f77; }
        QLabel { font-size: 13px; }
        """
        self.setStyleSheet(style)

    # ---------------- לוגיקה קיימת (ללא שינוי) ----------------
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
                self.toggle_mode()
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
