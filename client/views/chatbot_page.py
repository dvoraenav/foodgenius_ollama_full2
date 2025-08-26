from PySide6.QtWidgets import QWidget, QVBoxLayout
from components.ai_chat import AIChat

class ChatbotPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(AIChat())  # בלי recipe_id = צ'אט כללי
