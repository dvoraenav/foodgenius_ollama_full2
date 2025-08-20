# client/views/ai_chat_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout
from components.ai_chat import AIChat

class AIChatDialog(QDialog):
    def __init__(self, recipe_id: str | None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ask AI")
        self.setMinimumSize(520, 480)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)

        # משחילים לתוך הדיאלוג את הרכיב הקיים
        lay.addWidget(AIChat(recipe_id=recipe_id))
