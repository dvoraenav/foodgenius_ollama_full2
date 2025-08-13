from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QInputDialog, QMessageBox, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import requests, io
from presenters.recipe_presenter import RecipePresenter
from components.ai_chat import AIChat

class RecipeView(QDialog):
    def __init__(self, recipe_id: str, parent=None):
        super().__init__(parent)
        self.p = RecipePresenter(self)
        self.rid = recipe_id
        self.setMinimumSize(1000, 650)
        self.setWindowTitle("פרטי מתכון")

        self.title = QLabel("טוען…"); self.title.setStyleSheet("font-size:20px; font-weight:bold;"); self.title.setAlignment(Qt.AlignRight)
        self.nutrition = QLabel(""); self.nutrition.setAlignment(Qt.AlignRight)

        self.btn_vegan = QPushButton("הפוך לטבעוני"); self.btn_scale = QPushButton("שנה מנות…")
        self.btn_vegan_llm = QPushButton("הפוך לטבעוני (AI)"); self.btn_vegan_llm.setProperty("accent", True)
        self.btn_vegan.clicked.connect(self.make_vegan); self.btn_scale.clicked.connect(self.scale_servings); self.btn_vegan_llm.clicked.connect(self.make_vegan_llm)

        self.img_label = QLabel(); self.img_label.setFixedSize(420, 260); self.img_label.setAlignment(Qt.AlignCenter)
        self.ing_box = QTextEdit(); self.ing_box.setReadOnly(True)
        self.steps_box = QTextEdit(); self.steps_box.setReadOnly(True)

        top = QVBoxLayout(self)
        top.addWidget(self.title); top.addWidget(self.nutrition)
        row_btn = QHBoxLayout(); row_btn.addWidget(self.btn_vegan); row_btn.addWidget(self.btn_scale); row_btn.addWidget(self.btn_vegan_llm); row_btn.addStretch(1)
        top.addLayout(row_btn)

        row = QHBoxLayout()
        picCard = QFrame(); picCard.setProperty('class','card'); layPic = QVBoxLayout(picCard); layPic.addWidget(self.img_label); row.addWidget(picCard, 0)
        textCard = QFrame(); textCard.setProperty('class','card')
        layText = QVBoxLayout(textCard); layText.addWidget(QLabel("מרכיבים")); layText.addWidget(self.ing_box); layText.addWidget(QLabel("שלבים")); layText.addWidget(self.steps_box); row.addWidget(textCard, 1)
        top.addLayout(row)

        chatRow = QHBoxLayout(); chatRow.addWidget(AIChat(recipe_id), 1); top.addLayout(chatRow)
        self.load()

    def load(self):
        data = self.p.load(self.rid)
        self.title.setText(data.get("title",""))
        nutr = data.get("nutrition") or {}
        self.nutrition.setText(f"קלוריות: {int(nutr.get('cal',0))} | חלבון: {nutr.get('protein',0)} | שומן: {nutr.get('fat',0)} | פחמ': {nutr.get('carbs',0)}")
        url = data.get("image")
        if url:
            try:
                buf = requests.get(url, timeout=10).content
                pix = QPixmap(); pix.loadFromData(io.BytesIO(buf).read())
                self.img_label.setPixmap(pix.scaled(self.img_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            except Exception: self.img_label.setText("לא נטענה תמונה")
        self.ing_box.setText("\n".join(f"• {i.get('name')} {i.get('amount','')} {i.get('unit','')}".strip() for i in data.get("ingredients", [])))
        self.steps_box.setText("\n".join(f"{idx+1}. {s}" for idx, s in enumerate(data.get("steps", []))))

    def make_vegan(self):
        try:
            data = self.p.veganize(self.rid)["result"]
            self.title.setText(data.get("title", self.title.text()))
            self.ing_box.setText("\n".join(f"• {i.get('name')} {i.get('amount','')} {i.get('unit','')}".strip() for i in data["ingredients"]))
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", str(e))

    def make_vegan_llm(self):
        try:
            data = self.p.veganize_llm(self.rid)["result"]
            title = data.get("title") or (self.title.text()+" (LLM)")
            steps = data.get("steps") or []
            ingredients = data.get("ingredients") or []
            self.title.setText(title)
            if ingredients and isinstance(ingredients[0], str):
                self.ing_box.setText("\n".join(f"• {x}" for x in ingredients))
            else:
                self.ing_box.setText("\n".join(f"• {i.get('name')} {i.get('amount','')} {i.get('unit','')}".strip() for i in ingredients))
            self.steps_box.setText("\n".join(f"{idx+1}. {s}" for idx, s in enumerate(steps)))
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", str(e))

    def scale_servings(self):
        frm, ok1 = QInputDialog.getInt(self, "מנות קיימות", "כמה מנות במתכון המקורי?", 2, 1, 20, 1)
        if not ok1: return
        to, ok2 = QInputDialog.getInt(self, "שינוי מנות", "לכמה מנות להפוך?", 4, 1, 20, 1)
        if not ok2: return
        try:
            data = self.p.scale(self.rid, frm, to)["result"]
            self.ing_box.setText("\n".join(f"• {i.get('name')} {i.get('amount','')} {i.get('unit','')}".strip() for i in data["ingredients"]))
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", str(e))
