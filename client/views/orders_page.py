# client/views/orders_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QDialog, QListWidget, QListWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from services.api_client import ApiClient


class KitsDialog(QDialog):
    """דיאלוג בחירת קיט להזמנה"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("בחרי ערכת אוכל")
        self.setMinimumWidth(520)
        self.api = ApiClient()
        self.selected_kit = None

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("בחרי ערכה להזמנה:")
        title.setStyleSheet("font-weight:700;")
        root.addWidget(title)

        self.listw = QListWidget()
        self.listw.itemDoubleClicked.connect(self.accept_choose)
        root.addWidget(self.listw, 1)

        btns = QHBoxLayout()
        choose = QPushButton("בחרי")
        choose.setProperty("accent", True)
        choose.clicked.connect(self.accept_choose)
        cancel = QPushButton("ביטול")
        cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(choose)
        root.addLayout(btns)

        # טען קיטים
        try:
            kits = self.api.get("/orders/kits")
            self._kits = kits or []
            for k in self._kits:
                it = QListWidgetItem(f'{k["title"]} — ₪{k["price"]}  ·  {k.get("subtitle","")}')
                it.setData(Qt.UserRole, k)
                self.listw.addItem(it)
        except Exception as e:
            QMessageBox.warning(self, "שגיאה", f"טעינת קיטים נכשלה:\n{e}")

    def accept_choose(self):
        it = self.listw.currentItem()
        if not it:
            return
        self.selected_kit = it.data(Qt.UserRole)
        self.accept()


class OrderFormDialog(QDialog):
    """טופס פרטי הזמנה עבור קיט שנבחר"""
    def __init__(self, kit: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("פרטי הזמנה")
        self.setMinimumWidth(520)
        self.kit = kit

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        head = QLabel(f'🧺 {kit["title"]} — ₪{kit["price"]}')
        head.setStyleSheet("font-weight:700; font-size:15px;")
        root.addWidget(head)

        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet('QFrame[class="card"]{background:#fff;border:1px solid #e5e7eb;border-radius:12px;}')
        form = QFormLayout(card)
        form.setContentsMargins(12, 12, 12, 12)
        self.full_name = QLineEdit(); self.full_name.setPlaceholderText("שם מלא")
        self.phone = QLineEdit(); self.phone.setPlaceholderText("טלפון")
        self.address = QLineEdit(); self.address.setPlaceholderText("כתובת מלאה")
        self.notes = QTextEdit(); self.notes.setPlaceholderText("הערות (לא חובה)")
        form.addRow("שם מלא:", self.full_name)
        form.addRow("טלפון:", self.phone)
        form.addRow("כתובת:", self.address)
        form.addRow("הערות:", self.notes)
        root.addWidget(card)

        btns = QHBoxLayout()
        submit = QPushButton("שליחה")
        submit.setProperty("accent", True)
        submit.clicked.connect(self.validate_and_accept)
        cancel = QPushButton("ביטול")
        cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(submit)
        root.addLayout(btns)

    def validate_and_accept(self):
        if not self.full_name.text().strip() or not self.phone.text().strip() or not self.address.text().strip():
            QMessageBox.information(self, "חסר", "נא למלא שם מלא, טלפון וכתובת.")
            return
        self.accept()

    def payload(self) -> dict:
        return {
            "kit_id": self.kit["id"],
            "full_name": self.full_name.text().strip(),
            "phone": self.phone.text().strip(),
            "address": self.address.text().strip(),
            "notes": self.notes.toPlainText().strip(),
            # אפשר להוסיף user_email אם תרצי: "user_email": AUTH.user.get("email")
        }


class OrdersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api = ApiClient()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # כותרת + כפתורים
        header = QHBoxLayout()
        title = QLabel("🧺 ההזמנות שלי")
        title.setStyleSheet("font-weight:700; font-size:16px;")
        header.addWidget(title)
        header.addStretch(1)

        self.btn_browse = QPushButton("עיין בקיטים")
        self.btn_browse.setProperty("accent", True)
        header.addWidget(self.btn_browse)

        self.btn_refresh = QPushButton("רענון")
        header.addWidget(self.btn_refresh)

        root.addLayout(header)

        # טבלה להצגת הזמנות (שדות אמיתיים מהשרת)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["תאריך", "קיט", "מחיר (₪)", "שם מלא", "טלפון", "כתובת", "הערות"])
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table, 1)

        # חיבורים
        self.btn_browse.clicked.connect(self.browse_kits)
        self.btn_refresh.clicked.connect(self.load_orders)

        # טעינה ראשונית
        self.load_orders()

    # ----- UI actions -----
    def browse_kits(self):
        dlg = KitsDialog(self)
        if dlg.exec() != QDialog.Accepted or not dlg.selected_kit:
            return

        form = OrderFormDialog(dlg.selected_kit, self)
        if form.exec() == QDialog.Accepted:
            try:
                self.api.post("/orders", json=form.payload())
                QMessageBox.information(self, "נשמר", "ההזמנה נקלטה בהצלחה.")
                self.load_orders()
            except Exception as e:
                QMessageBox.warning(self, "שגיאה", f"לא ניתן לשמור הזמנה:\n{e}")

    def load_orders(self):
        try:
            rows = self.api.get("/orders") or []
        except Exception as e:
            QMessageBox.warning(self, "שגיאה", f"טעינת הזמנות נכשלה:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            # התאמה לשמות השדות מהשרת (OrderOut)
            self._set(i, 0, r.get("created_at", ""))
            self._set(i, 1, r.get("kit_title", ""))
            self._set(i, 2, str(r.get("price", "")))
            self._set(i, 3, r.get("full_name", ""))
            self._set(i, 4, r.get("phone", ""))
            self._set(i, 5, r.get("address", ""))
            self._set(i, 6, r.get("notes", ""))

    def _set(self, row: int, col: int, text: str):
        self.table.setItem(row, col, QTableWidgetItem(str(text)))
