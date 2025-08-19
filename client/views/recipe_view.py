from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from services.api_client import ApiClient

class RecipeView(QDialog):
    def __init__(self, rid: str, parent=None):
        super().__init__(parent)
        self.api = ApiClient()
        self.setWindowTitle("מתכון מלא")
        self.setMinimumSize(600, 500)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.title_label = QLabel("🔄 טוען מתכון...")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(200)
        self.layout.addWidget(self.image_label)

        self.ing_list = QListWidget()
        self.layout.addWidget(QLabel("🧾 רכיבים:"))
        self.layout.addWidget(self.ing_list)

        self.steps_area = QTextEdit()
        self.steps_area.setReadOnly(True)
        self.layout.addWidget(QLabel("🧑‍🍳 שלבים:"))
        self.layout.addWidget(self.steps_area)

        self.load(rid)

    def load(self, rid: str):
        recipe = self.api.get_external_recipe_by_id(rid)
        if not recipe:
            self.title_label.setText("❌ מתכון לא נמצא")
            return

        self.title_label.setText(recipe.get("title", "ללא שם"))

        # תמונה
        img_url = recipe.get("image")
        if img_url:
            try:
                from requests import get
                pix = QPixmap()
                pix.loadFromData(get(img_url, timeout=10).content)
                self.image_label.setPixmap(pix.scaledToHeight(200, Qt.SmoothTransformation))
            except Exception:
                self.image_label.setText("לא נטענה תמונה")

        # רכיבים
        self.ing_list.clear()
        for ing in recipe.get("ingredients", []):
            name = ing.get("name", "")
            amount = ing.get("amount", "")
            text = f"{name} - {amount}" if amount else name
            self.ing_list.addItem(QListWidgetItem(text))

        # שלבים
        steps = recipe.get("steps", [])
        steps_text = "\n".join(f"{idx+1}. {step}" for idx, step in enumerate(steps))
        self.steps_area.setText(steps_text if steps_text else "אין שלבים זמינים.")
