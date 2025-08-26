from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from services.api_client import ApiClient
from components.ai_chat import AIChat
from components.nutrition_chart import NutritionChart, calculate_nutrition_from_ingredients

class RecipePage(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api = ApiClient()
        self.recipe_id = None
        self.recipe = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # בר עליון: חזרה + כפתורי עזרה
        top = QHBoxLayout()
        self.btn_back = QPushButton("← Back to recipes")
        self.btn_back.clicked.connect(self.back_requested.emit)

        self.btn_ai = QPushButton("Ask AI")
        self.btn_ai.setProperty("accent", True)
        self.btn_ai.clicked.connect(self.toggle_ai)

        self.btn_nutri = QPushButton("Nutrition")
        self.btn_nutri.setProperty("accent", True)
        self.btn_nutri.clicked.connect(self.toggle_nutrition)

        top.addWidget(self.btn_back, 0, Qt.AlignLeft)
        top.addStretch(1)
        top.addWidget(self.btn_ai)
        top.addWidget(self.btn_nutri)
        root.addLayout(top)

        # גלילה לתוכן
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        root.addWidget(self.scroll, 1)

        self.wrap = QWidget()
        self.scroll.setWidget(self.wrap)
        self.body = QVBoxLayout(self.wrap)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(10)

        # כותרת
        self.title = QLabel("")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:20px; font-weight:700;")
        self.body.addWidget(self.title)

        # תמונה
        self.img = QLabel()
        self.img.setObjectName("Hero")
        self.img.setFixedHeight(240)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("QLabel#Hero{border-radius:12px; background:#f3f4f6;}")
        self.body.addWidget(self.img)

        # כרטיס רכיבים
        self.ing_card = QFrame(); self.ing_card.setProperty("class","card")
        self.ing_card.setStyleSheet('QFrame[class="card"]{background:#fff;border:1px solid #e5e7eb;border-radius:16px;}')
        ing_box = QVBoxLayout(self.ing_card); ing_box.setContentsMargins(12,12,12,12)
        ing_title = QLabel("Ingredients"); ing_title.setStyleSheet("font-weight:700;")
        self.ing_list = QListWidget()
        ing_box.addWidget(ing_title); ing_box.addWidget(self.ing_list)
        self.body.addWidget(self.ing_card)

        # כרטיס שלבים
        self.steps_card = QFrame(); self.steps_card.setProperty("class","card")
        self.steps_card.setStyleSheet('QFrame[class="card"]{background:#fff;border:1px solid #e5e7eb;border-radius:16px;}')
        st_box = QVBoxLayout(self.steps_card); st_box.setContentsMargins(12,12,12,12)
        st_title = QLabel("Steps"); st_title.setStyleSheet("font-weight:700;")
        self.steps_label = QLabel(""); self.steps_label.setWordWrap(True)
        st_box.addWidget(st_title); st_box.addWidget(self.steps_label)
        self.body.addWidget(self.steps_card)

        # פאנלים נסתרים: AI + Nutrition
        self.ai_panel = AIChat(recipe_id=None); self.ai_panel.setVisible(False)
        self.body.addWidget(self.ai_panel)

        self.nutri_panel = NutritionChart(nutrition_data=None); self.nutri_panel.setVisible(False)
        self.body.addWidget(self.nutri_panel)

    # ------- API / טעינה -------
    def load_recipe(self, recipe_id: str):
        """קורא מהשרת ומציג, כולל תמונה/רכיבים/שלבים"""
        self.recipe_id = recipe_id
        self.ai_panel.recipe_id = recipe_id  # שירוץ על ההקשר הנכון

        rec = self.api.get_external_recipe_by_id(recipe_id) or {}
        self.recipe = rec

        # כותרת
        self.title.setText(rec.get("title", "Untitled"))

        # תמונה
        self.img.clear()
        url = rec.get("image")
        if url:
            try:
                import requests
                p = QPixmap(); p.loadFromData(requests.get(url, timeout=10).content)
                if not p.isNull():
                    self.img.setPixmap(p.scaled(self.img.width(), self.img.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            except Exception:
                self.img.setText("No image")

        # רכיבים
        self.ing_list.clear()
        for ing in rec.get("ingredients", []):
            name = ing.get("name","").strip()
            amt  = ing.get("amount","").strip()
            self.ing_list.addItem(QListWidgetItem(f"{name}" + (f" — {amt}" if amt else "")))

        # שלבים
        steps = rec.get("steps") or rec.get("instructions") or []
        if isinstance(steps, str):
            steps = [s.strip() for s in steps.split(".") if s.strip()]
        text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
        self.steps_label.setText(text or "No steps available.")

        # סגירת פאנלים אם היו פתוחים
        self.ai_panel.setVisible(False)
        self.nutri_panel.setVisible(False)

    # ------- כפתורים -------
    def toggle_ai(self):
        self.ai_panel.setVisible(not self.ai_panel.isVisible())

    def toggle_nutrition(self):
        if not self.nutri_panel.isVisible():
            # אם אין – חשב והצג
            data = calculate_nutrition_from_ingredients(self.recipe.get("ingredients", []))
            self.nutri_panel.update_nutrition_data(data)
        self.nutri_panel.setVisible(not self.nutri_panel.isVisible())
