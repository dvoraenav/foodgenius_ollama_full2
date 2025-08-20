# client/views/recipe_view.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QListWidget, QListWidgetItem,
    QWidget, QHBoxLayout, QFrame, QPushButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import requests
from services.api_client import ApiClient

class RecipeView(QDialog):
    def __init__(self, rid: str, parent=None):
        super().__init__(parent)
        self.api = ApiClient()
        self.recipe_id = rid

        self.setWindowTitle("Full Recipe")
        self.setMinimumSize(760, 600)
        self.setLayoutDirection(Qt.LeftToRight)  # הכל לשמאל/אנגלית

        root = QVBoxLayout(self)
        root.setContentsMargins(10,10,10,10)
        root.setSpacing(10)

        # ===== Header: Button (left) + Centered Title + dummy spacer (right) =====
        header = QHBoxLayout()
        self.btn_ai = QPushButton("Ask AI")
        self.btn_ai.setProperty("accent", True)
        self.btn_ai.clicked.connect(self.open_ai)
        header.addWidget(self.btn_ai, 0, Qt.AlignLeft)

        self.title_label = QLabel("Loading…")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size:22px; font-weight:800;")
        header.addWidget(self.title_label, 1)

        # spacer עם רוחב כפתור, כדי שהכותרת באמת תהיה באמצע
        self._right_spacer = QLabel("")
        self._right_spacer.setFixedWidth(self.btn_ai.sizeHint().width())
        header.addWidget(self._right_spacer, 0, Qt.AlignRight)

        root.addLayout(header)

        # ===== Banner image (fills width) with smart cover/contain =====
        self.banner = QWidget()
        self.banner.setFixedHeight(240)
        self.banner.setStyleSheet("background:#0f172a; border-radius:12px;")
        root.addWidget(self.banner)

        self.img = QLabel(self.banner)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setGeometry(0, 0, self.banner.width(), self.banner.height())
        self.img.setStyleSheet("border:0;")
        self._orig = None

        def _resize_banner(e):
            self.img.setGeometry(0, 0, self.banner.width(), self.banner.height())
            if self._orig: self._apply_smart()
            QWidget.resizeEvent(self.banner, e)
        self.banner.resizeEvent = _resize_banner

        # ===== Ingredients card =====
        root.addWidget(self._section_title("Ingredients:"))
        ing_card = QFrame(); ing_card.setProperty("class","card")
        ing_card.setStyleSheet('QFrame[class="card"]{background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;}')
        ing_lay = QVBoxLayout(ing_card); ing_lay.setContentsMargins(10,10,10,10)
        self.ing_list = QListWidget()
        self.ing_list.setLayoutDirection(Qt.LeftToRight)
        ing_lay.addWidget(self.ing_list)
        root.addWidget(ing_card)

        # ===== Steps card =====
        root.addWidget(self._section_title("Steps:"))
        steps_card = QFrame(); steps_card.setProperty("class","card")
        steps_card.setStyleSheet('QFrame[class="card"]{background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;}')
        st_lay = QVBoxLayout(steps_card); st_lay.setContentsMargins(10,10,10,10)
        self.steps_area = QTextEdit(); self.steps_area.setReadOnly(True)
        self.steps_area.setLayoutDirection(Qt.LeftToRight)
        self.steps_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        st_lay.addWidget(self.steps_area)
        root.addWidget(steps_card, 1)

        self.load(rid)

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignLeft)
        lbl.setStyleSheet("color:#374151; font-weight:700;")
        return lbl

    def _apply_smart(self):
        """Smart cover: אם הקרופ גדול מדי – עוברים ל-contain."""
        W, H = max(1, self.img.width()), max(1, self.img.height())
        pw, ph = self._orig.width(), self._orig.height()
        s_cover = max(W/pw, H/ph)
        if s_cover > 1.35:
            scaled = self._orig.scaled(W, H, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # contain
        else:
            scaled = self._orig.scaled(W, H, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)  # cover
        self.img.setPixmap(scaled)

    def load(self, rid: str):
        rec = self.api.get_external_recipe_by_id(rid)
        if not rec:
            self.title_label.setText("Recipe not found")
            self.btn_ai.setEnabled(False)
            return

        self.title_label.setText(rec.get("title",""))

        # image
        url = rec.get("image")
        if url:
            try:
                r = requests.get(url, timeout=10); r.raise_for_status()
                pix = QPixmap(); pix.loadFromData(r.content)
                self._orig = pix; self._apply_smart()
            except Exception:
                self.img.setText("No image")
        else:
            self.img.setText("No image")

        # ingredients
        self.ing_list.clear()
        for ing in rec.get("ingredients") or []:
            name = (ing.get("name") or "").strip()
            amt  = (ing.get("amount") or "").strip()
            it = QListWidgetItem(f"{name} - {amt}" if amt else name)
            it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.ing_list.addItem(it)

        # steps
        steps = rec.get("steps") or []
        steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)) or "No steps available."
        self.steps_area.setPlainText(steps_text)
    def open_ai(self):
        # נסי להשתמש בדיאלוג הייעודי אם קיים
        try:
            from views.ai_chat_dialog import AIChatDialog
            AIChatDialog(recipe_id=self.recipe_id, parent=self).exec()
            return
        except ImportError:
            pass  # אין דיאלוג ייעודי – ניפול לפאלבק

        # פאלבק: דיאלוג רגיל עם הווידג'ט AIChat
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        from components.ai_chat import AIChat

        dlg = QDialog(self)
        dlg.setWindowTitle("Ask AI")
        lay = QVBoxLayout(dlg)
        lay.addWidget(AIChat(recipe_id=self.recipe_id))
        dlg.resize(520, 480)
        dlg.exec()

