from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QWidget, QScrollArea
)
from PySide6.QtCore import Qt
from presenters.recipe_presenter import RecipePresenter


class AIChat(QFrame):
    def __init__(self, recipe_id: str | None = None):
        super().__init__()
        self.p = RecipePresenter(self)
        self.recipe_id = recipe_id
        self.setProperty("class", "card")

        # תצוגת הודעות
        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)

        scroll_content = QWidget()
        scroll_content.setLayout(self.chat_area)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(scroll_content)
        self.scroll.setStyleSheet("background: #f9fafb; border: none;")

        # קלט
        self.inp = QTextEdit()
        self.inp.setPlaceholderText("שאלי כל דבר על המתכון…")
        self.btn = QPushButton("שליחה")
        self.btn.setProperty("accent", True)
        self.btn.clicked.connect(self.ask)

        # פריסה כללית
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(QLabel("🤖 עוזר בישול (AI)"), 0, Qt.AlignRight)
        layout.addWidget(self.scroll, 1)
        layout.addWidget(self.inp)
        layout.addWidget(self.btn)

    def append_bubble(self, text, is_user: bool):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(f"""
            background: {'#dbeafe' if is_user else '#dcfce7'};
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            max-width: 75%;
        """)
        hlayout = QHBoxLayout()
        if is_user:
            hlayout.addStretch()
            hlayout.addWidget(label)
        else:
            hlayout.addWidget(label)
            hlayout.addStretch()
        self.chat_area.insertLayout(self.chat_area.count() - 1, hlayout)

        # גלילה אוטומטית לתחתית
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def ask(self):
        q = self.inp.toPlainText().strip()
        if not q:
            return

        self.append_bubble(q, is_user=True)
        self.inp.clear()

        try:
            data = self.p.chat(self.recipe_id, q)
            ans = data.get("answer", "(לא התקבלה תשובה)")
            self.append_bubble(ans, is_user=False)
        except Exception as e:
            self.append_bubble(f"[שגיאה] {e}", is_user=False)
