from PySide6.QtWidgets import QFrame, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
from presenters.recipe_presenter import RecipePresenter

class AIChat(QFrame):
    def __init__(self, recipe_id: str | None = None):
        super().__init__()
        self.p = RecipePresenter(self)
        self.recipe_id = recipe_id
        self.setProperty("class", "card")

        self.out = QTextEdit(); self.out.setReadOnly(True)
        self.inp = QTextEdit(); self.inp.setPlaceholderText("שאלי כל דבר על המתכון…")
        self.btn = QPushButton("שליחה"); self.btn.setProperty("accent", True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12,12,12,12)
        lay.addWidget(QLabel("עוזר בישול (AI)"), 0, Qt.AlignRight)
        lay.addWidget(self.out, 1)
        lay.addWidget(self.inp)
        lay.addWidget(self.btn)

        self.btn.clicked.connect(self.ask)

    def ask(self):
        q = self.inp.toPlainText().strip()
        if not q:
            print("❌ לא הוזנה שאלה.")
            return

        print(f"📤 שאלה נשלחת לשרת: {q}")
        try:
            data = self.p.chat(self.recipe_id, q)
            print("✅ תשובה שהתקבלה מהשרת:", data)
            ans = data.get("answer", "")
            self.out.append(f"את: {q}\nAI: {ans}\n")
            self.inp.clear()
        except Exception as e:
            print("❌ שגיאה:", e)
            self.out.append(f"[שגיאה] {e}")

