# client/views/orders_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QGridLayout, QFrame, QLineEdit, QTextEdit, QFormLayout, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import requests

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
        self.img.setGeometry(0,0,banner.width(),banner.height())
        banner.resizeEvent = lambda e: (self.img.setGeometry(0,0,banner.width(),banner.height()), QFrame.resizeEvent(banner,e))

        url = kit.get("image")
        if url:
            try:
                r = requests.get(url, timeout=8); r.raise_for_status()
                p = QPixmap(); p.loadFromData(r.content)
                if not p.isNull():
                    self.img.setPixmap(p.scaled(self.img.width() or 1, self.img.height() or 1,
                                                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
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
    """עמוד יחיד – בחירת ערכה -> טופס -> הצלחה (בלי דיאלוגים, בלי טבלה)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api = ApiClient()
        self._selected_kit: dict | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(10)

        # כותרת עליונה
        header = QHBoxLayout()
        title = QLabel("🧺 הזמנת ערכת אוכל")
        title.setStyleSheet("font-weight:700;font-size:16px;")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        # סטאק פנימי של המצבים
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        # --- מצב 1: גריד קיטים ---
        self.page_grid = QWidget()
        grid_wrap = QVBoxLayout(self.page_grid); grid_wrap.setContentsMargins(0,0,0,0); grid_wrap.setSpacing(8)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.grid_host = QWidget(); self.grid = QGridLayout(self.grid_host)
        self.grid.setHorizontalSpacing(14); self.grid.setVerticalSpacing(14)
        self.scroll.setWidget(self.grid_host)
        grid_wrap.addWidget(self.scroll, 1)

        self.stack.addWidget(self.page_grid)

        # --- מצב 2: טופס הזמנה לקיט שנבחר ---
        self.page_form = QWidget()
        form_root = QVBoxLayout(self.page_form); form_root.setSpacing(10)

        self.form_kit_title = QLabel(""); self.form_kit_title.setStyleSheet("font-weight:700;font-size:15px;")
        form_root.addWidget(self.form_kit_title)

        card = QFrame(); card.setProperty("class","card")
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

        btn_row = QHBoxLayout()
        self.btn_back_to_grid = QPushButton("חזרה");
        self.btn_submit = QPushButton("שליחת הזמנה"); self.btn_submit.setProperty("accent", True)
        btn_row.addStretch(1); btn_row.addWidget(self.btn_back_to_grid); btn_row.addWidget(self.btn_submit)
        form_root.addLayout(btn_row)

        self.stack.addWidget(self.page_form)

        # --- מצב 3: הצלחה ---
        self.page_done = QWidget()
        done_root = QVBoxLayout(self.page_done); done_root.setAlignment(Qt.AlignCenter)
        lbl_ok = QLabel("✅ ההזמנה נקלטה בהצלחה!")
        lbl_ok.setStyleSheet("font-weight:700;font-size:18px;")
        btn_again = QPushButton("להזמין ערכה נוספת")
        btn_again.setProperty("accent", True)
        done_root.addWidget(lbl_ok)
        done_root.addWidget(btn_again)
        self.stack.addWidget(self.page_done)

        # חיבורים
        self.btn_back_to_grid.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_grid))
        self.btn_submit.clicked.connect(self.submit_order)
        btn_again.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_grid))

        # טעינת קיטים
        self.load_kits()
        self.stack.setCurrentWidget(self.page_grid)

    # ---------- גריד קיטים ----------
    def load_kits(self):
        # נקה
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w: w.deleteLater()

        kits = []
        try:
            kits = self.api.get("/orders/kits") or []
        except Exception as e:
            # מציגים הודעה מינימלית במקום QMessageBox כדי להישאר "עמוד יחיד"
            err = QLabel(f"שגיאה בטעינת קיטים: {e}")
            err.setStyleSheet("color:#ef4444;")
            self.grid.addWidget(err, 0, 0)
            return

        for i, k in enumerate(kits):
            self.grid.addWidget(KitCard(k, self.start_order), i // 3, i % 3)

    def start_order(self, kit: dict):
        self._selected_kit = kit
        self.form_kit_title.setText(f'🧺 {kit.get("title","")} — ₪{kit.get("price",0)}')
        # אפס שדות
        self.in_fullname.setText("")
        self.in_phone.setText("")
        self.in_address.setText("")
        self.in_notes.setPlainText("")
        self.stack.setCurrentWidget(self.page_form)

    # ---------- שליחת הזמנה ----------
    def submit_order(self):
        if not self._selected_kit:
            return
        fn = self.in_fullname.text().strip()
        ph = self.in_phone.text().strip()
        ad = self.in_address.text().strip()
        if not fn or not ph or not ad:
            # הודעה קטנה בתוך העמוד
            if not hasattr(self, "_warn"):
                self._warn = QLabel(""); self._warn.setStyleSheet("color:#ef4444;")
                self.page_form.layout().addWidget(self._warn)
            self._warn.setText("נא למלא שם, טלפון וכתובת.")
            return
        if hasattr(self, "_warn"):
            self._warn.setText("")

        payload = {
            "kit_id": self._selected_kit["id"],
            "full_name": fn,
            "phone": ph,
            "address": ad,
            "notes": self.in_notes.toPlainText().strip(),
        }
        # אם יש משתמש מחובר – נשמור את האימייל להזמנה
        try:
            if getattr(AUTH, "user", None):
                email = AUTH.user.get("email")
                if email:
                    payload["user_email"] = email
        except Exception:
            pass

        try:
            self.api.post("/orders", json=payload)
            self.stack.setCurrentWidget(self.page_done)
        except Exception as e:
            if not hasattr(self, "_warn"):
                self._warn = QLabel(""); self._warn.setStyleSheet("color:#ef4444;")
                self.page_form.layout().addWidget(self._warn)
            self._warn.setText(f"שגיאה בשליחה: {e}")
