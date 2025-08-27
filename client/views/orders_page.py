# client/views/orders_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QGridLayout, QFrame, QLineEdit, QTextEdit, QFormLayout, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import requests
from datetime import datetime

from services.api_client import ApiClient
from services.auth import AUTH


class KitCard(QFrame):
    """כרטיס ערכה לתצוגת הגריד"""
    def __init__(self, kit: dict, on_order):
        super().__init__()
        self.kit = kit
        self.setProperty("class", "card")
        self.setStyleSheet('''
            QFrame[class="card"]{background:#fff;border:1px solid #e5e7eb;border-radius:16px;}
            QLabel[class="title"]{font-weight:700;font-size:14px;}
            QPushButton[accent="true"]{background:#10b981;color:white;border:none;border-radius:10px;padding:8px 12px;font-weight:600;}
            QPushButton[accent="true"]:hover{background:#059669;}
        ''')

        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(8)

        # תמונה
        banner = QFrame()
        banner.setFixedHeight(140)
        banner.setStyleSheet("background:#0f172a;border-top-left-radius:16px;border-top-right-radius:16px;")
        root.addWidget(banner)

        self.img = QLabel(banner)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setGeometry(0, 0, banner.width(), banner.height())
        banner.resizeEvent = lambda e: (
            self.img.setGeometry(0,0,banner.width(),banner.height()),
            QFrame.resizeEvent(banner, e)
        )

        url = kit.get("image")
        if url:
            try:
                r = requests.get(url, timeout=8); r.raise_for_status()
                p = QPixmap(); p.loadFromData(r.content)
                if not p.isNull():
                    self.img.setPixmap(
                        p.scaled(self.img.width() or 1, self.img.height() or 1,
                                 Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    )
            except Exception:
                self.img.setText("")

        # תוכן
        body = QVBoxLayout()
        body.setContentsMargins(12,8,12,12)
        body.setSpacing(6)
        root.addLayout(body)

        title = QLabel(kit.get("title","")); title.setProperty("class","title"); title.setWordWrap(True)
        body.addWidget(title)

        sub = QLabel(kit.get("subtitle",""))
        sub.setStyleSheet("color:#6b7280;")
        body.addWidget(sub)

        price = QLabel(f'₪{kit.get("price",0)}')
        price.setStyleSheet("font-weight:700;")
        body.addWidget(price)

        body.addStretch(1)

        btn = QPushButton("הזמנה"); btn.setProperty("accent", True)
        btn.clicked.connect(lambda: on_order(kit))
        body.addWidget(btn)


class OrdersPage(QWidget):
    """עמוד אחד: גריד קיטים → טופס הזמנה (לקוח + תשלום דמו) → הצלחה"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api = ApiClient()
        self._selected_kit: dict | None = None
        self._warn: QLabel | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(10)

        # כותרת
        header = QHBoxLayout()
        title = QLabel("🧺 הזמנת ערכת אוכל")
        title.setStyleSheet("font-weight:700;font-size:16px;")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        # סטאק פנימי
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        # ===== מצב 1: גריד קיטים =====
        self.page_grid = QWidget()
        grid_wrap = QVBoxLayout(self.page_grid); grid_wrap.setContentsMargins(0,0,0,0); grid_wrap.setSpacing(8)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setHorizontalSpacing(14); self.grid.setVerticalSpacing(14)
        self.scroll.setWidget(self.grid_host)
        grid_wrap.addWidget(self.scroll, 1)

        self.stack.addWidget(self.page_grid)

        # ===== מצב 2: טופס הזמנה =====
        self.page_form = QWidget()
        form_root = QVBoxLayout(self.page_form); form_root.setSpacing(10)

        self.form_kit_title = QLabel("")
        self.form_kit_title.setStyleSheet("font-weight:700;font-size:15px;")
        form_root.addWidget(self.form_kit_title)

        # --- כרטיס פרטי לקוח ---
        card = QFrame(); card.setProperty("class", "card")
        card.setStyleSheet('QFrame[class="card"]{background:#fff;border:1px solid #e5e7eb;border-radius:12px;}')
        form = QFormLayout(card); form.setContentsMargins(12,12,12,12)

        self.in_fullname = QLineEdit(); self.in_fullname.setPlaceholderText("שם מלא")
        self.in_phone    = QLineEdit(); self.in_phone.setPlaceholderText("טלפון")
        self.in_address  = QLineEdit(); self.in_address.setPlaceholderText("כתובת מלאה")
        self.in_notes    = QTextEdit(); self.in_notes.setPlaceholderText("הערות (לא חובה)")

        form.addRow("שם מלא:", self.in_fullname)
        form.addRow("טלפון:", self.in_phone)
        form.addRow("כתובת:", self.in_address)
        form.addRow("הערות:", self.in_notes)
        form_root.addWidget(card)

        # --- כרטיס פרטי תשלום (דמו) ---
        pay_title = QLabel("פרטי תשלום")
        pay_title.setStyleSheet("font-weight:700;")
        form_root.addWidget(pay_title)

        pay_card = QFrame(); pay_card.setProperty("class","card")
        pay_card.setStyleSheet('QFrame[class="card"]{background:#fff;border:1px solid #e5e7eb;border-radius:12px;}')
        pay_form = QFormLayout(pay_card); pay_form.setContentsMargins(12,12,12,12)

        self.in_holder = QLineEdit(); self.in_holder.setPlaceholderText("שם בעל/ת הכרטיס")
        self.in_card   = QLineEdit(); self.in_card.setInputMask("0000 0000 0000 0000;_"); self.in_card.setPlaceholderText("1234 5678 9012 3456")
        self.in_exp    = QLineEdit(); self.in_exp.setInputMask("00/00;_"); self.in_exp.setPlaceholderText("MM/YY")
        self.in_cvv    = QLineEdit(); self.in_cvv.setEchoMode(QLineEdit.Password); self.in_cvv.setInputMask("0000;_"); self.in_cvv.setPlaceholderText("3-4 ספרות")

        pay_form.addRow("שם על הכרטיס:", self.in_holder)
        pay_form.addRow("מספר כרטיס:", self.in_card)
        pay_form.addRow("תוקף (MM/YY):", self.in_exp)
        pay_form.addRow("CVV:", self.in_cvv)
        form_root.addWidget(pay_card)

        # אזהרה/שגיאה אינליין
        self._warn = QLabel(""); self._warn.setStyleSheet("color:#ef4444;")
        form_root.addWidget(self._warn)

        # כפתורים
        btn_row = QHBoxLayout()
        self.btn_back_to_grid = QPushButton("חזרה")
        self.btn_submit = QPushButton("שליחת הזמנה"); self.btn_submit.setProperty("accent", True)
        btn_row.addStretch(1); btn_row.addWidget(self.btn_back_to_grid); btn_row.addWidget(self.btn_submit)
        form_root.addLayout(btn_row)

        self.stack.addWidget(self.page_form)

        # ===== מצב 3: הצלחה =====
        self.page_done = QWidget()
        done_root = QVBoxLayout(self.page_done); done_root.setAlignment(Qt.AlignCenter)
        lbl_ok = QLabel("✅ ההזמנה נקלטה בהצלחה!")
        lbl_ok.setStyleSheet("font-weight:700;font-size:18px;")
        btn_again = QPushButton("להזמין ערכה נוספת"); btn_again.setProperty("accent", True)
        done_root.addWidget(lbl_ok); done_root.addWidget(btn_again)
        self.stack.addWidget(self.page_done)

        # חיבורים
        self.btn_back_to_grid.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_grid))
        self.btn_submit.clicked.connect(self.submit_order)
        btn_again.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_grid))

        # טעינה ראשונית
        self.load_kits()
        self.stack.setCurrentWidget(self.page_grid)

    # ---------- גריד קיטים ----------
    def load_kits(self):
        # נקה גריד
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w: w.deleteLater()

        try:
            kits = self.api.get("/orders/kits") or []
        except Exception as e:
            err = QLabel(f"שגיאה בטעינת קיטים: {e}")
            err.setStyleSheet("color:#ef4444;")
            self.grid.addWidget(err, 0, 0)
            return

        for i, k in enumerate(kits):
            self.grid.addWidget(KitCard(k, self.start_order), i // 3, i % 3)

    # ---------- מעבר לטופס ----------
    def start_order(self, kit: dict):
        self._selected_kit = kit
        self.form_kit_title.setText(f'🧺 {kit.get("title","")} — ₪{kit.get("price",0)}')

        # איפוס שדות לקוח
        self.in_fullname.setText("")
        self.in_phone.setText("")
        self.in_address.setText("")
        self.in_notes.setPlainText("")

        # איפוס תשלום
        self.in_holder.setText("")
        self.in_card.setText("")
        self.in_exp.setText("")
        self.in_cvv.setText("")

        self._warn.setText("")
        self.stack.setCurrentWidget(self.page_form)

    # ---------- בדיקות ----------
    def _show_warn(self, msg: str):
        self._warn.setText(msg)

    def _validate_customer(self) -> bool:
        if not self.in_fullname.text().strip() or not self.in_phone.text().strip() or not self.in_address.text().strip():
            self._show_warn("נא למלא שם, טלפון וכתובת.")
            return False
        return True

    def _validate_payment_demo(self) -> bool:
        """בדיקות דמו בסיסיות בלבד – לא נשלח לשרת"""
        holder = self.in_holder.text().strip()
        card_digits = ''.join(ch for ch in self.in_card.text() if ch.isdigit())
        exp = self.in_exp.text().strip()
        cvv = ''.join(ch for ch in self.in_cvv.text() if ch.isdigit())

        if not holder or len(card_digits) not in (15, 16) or len(cvv) not in (3, 4):
            self._show_warn("בדקי פרטי תשלום: שם, כרטיס (15-16 ספרות), CVV (3-4).")
            return False

        # תוקף
        try:
            mm, yy = exp.split("/")
            mm = int(mm); yy = int(yy) + 2000
            if not (1 <= mm <= 12): raise ValueError
            # סוף-חודש של התוקף
            exp_dt = datetime(yy, mm, 1)
            now = datetime.now()
            if exp_dt.year < now.year or (exp_dt.year == now.year and exp_dt.month < now.month):
                self._show_warn("כרטיס שפג תוקפו.")
                return False
        except Exception:
            self._show_warn("תוקף לא תקין (MM/YY).")
            return False

        self._show_warn("")
        return True

    # ---------- שליחה ----------
    def submit_order(self):
        if not self._selected_kit:
            return
        if not self._validate_customer():
            return
        if not self._validate_payment_demo():
            return

        payload = {
            "kit_id": self._selected_kit["id"],
            "full_name": self.in_fullname.text().strip(),
            "phone": self.in_phone.text().strip(),
            "address": self.in_address.text().strip(),
            "notes": self.in_notes.toPlainText().strip(),
        }

        # אם יש משתמש – שמירת אימייל להזמנה
        try:
            if getattr(AUTH, "user", None):
                email = AUTH.user.get("email")
                if email:
                    payload["user_email"] = email
        except Exception:
            pass

        try:
            # אל שולחים פרטי כרטיס! רק את ההזמנה.
            self.api.post("/orders", json=payload)
            self.stack.setCurrentWidget(self.page_done)
        except Exception as e:
            self._show_warn(f"שגיאה בשליחה: {e}")
