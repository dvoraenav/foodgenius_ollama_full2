from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QWidget, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QEvent
from presenters.recipe_presenter import RecipePresenter


class _ChatWorker(QThread):
    done = Signal(dict)
    fail = Signal(str)

    def __init__(self, presenter, recipe_id, question):
        super().__init__()
        self.presenter = presenter
        self.recipe_id = recipe_id
        self.question = question

    def run(self):
        try:
            data = self.presenter.chat(self.recipe_id, self.question)
            self.done.emit(data or {})
        except Exception as e:
            self.fail.emit(str(e))


class AIChat(QFrame):
    def __init__(self, recipe_id: str | None = None):
        super().__init__()
        self.p = RecipePresenter(self)
        self.recipe_id = recipe_id
        self.setProperty("class", "card")
        self._busy = False
        self._worker = None
        self._typing_lbl = None

        # --- כותרת + ניקוי ---
        header = QHBoxLayout()
        title = QLabel("🤖 עוזר בישול (AI)")
        header.addWidget(title, 1, Qt.AlignLeft)
        self.btn_clear = QPushButton("ניקוי")
        self.btn_clear.clicked.connect(self.clear_chat)
        header.addWidget(self.btn_clear, 0, Qt.AlignRight)

        # --- תצוגת הודעות (לוקחת את רוב הגובה) ---
        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)
        scroll_content = QWidget()
        scroll_content.setLayout(self.chat_area)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(scroll_content)
        self.scroll.setStyleSheet("background:#f9fafb; border:none;")

        # --- אזור קלט קטן + כפתור בשורה אחת ---
        self.inp = QTextEdit()
        self.inp.setPlaceholderText("שאלי כל דבר על המתכון… (Ctrl+Enter לשליחה)")
        self.inp.setFixedHeight(72)
        self.inp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn = QPushButton("שליחה")
        self.btn.setProperty("accent", True)
        self.btn.setFixedHeight(44)
        self.btn.setMinimumWidth(110)

        send_bar = QHBoxLayout()
        send_bar.addWidget(self.inp, 1)
        send_bar.addWidget(self.btn, 0)

        # --- פריסה כללית ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addLayout(header)
        layout.addWidget(self.scroll)       # תופס את רוב הגובה
        layout.addLayout(send_bar)
        layout.setStretch(1, 1)             # נותן עדיפות לגובה ה-scroll

        # --- חיבורים ---
        self.btn.clicked.connect(self.ask)
        self.inp.installEventFilter(self)   # Ctrl+Enter לשליחה

    # שליחה ב־Ctrl+Enter
    def eventFilter(self, obj, ev):
        if obj is self.inp and ev.type() == QEvent.KeyPress:
            if (ev.modifiers() & Qt.ControlModifier) and ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.ask()
                return True
        return super().eventFilter(obj, ev)

    def append_bubble(self, text: str, is_user: bool):
        label = QLabel(text or "")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(f"""
            background: {'#dbeafe' if is_user else '#dcfce7'};
            border-radius: 12px; padding: 8px 12px; margin: 4px; max-width: 75%;
        """)
        line = QHBoxLayout()
        if is_user:
            line.addStretch()
            line.addWidget(label)
        else:
            line.addWidget(label)
            line.addStretch()
        self.chat_area.insertLayout(self.chat_area.count() - 1, line)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def set_busy(self, busy: bool):
        self._busy = busy
        self.btn.setEnabled(not busy)
        self.inp.setEnabled(not busy)
        self.btn_clear.setEnabled(not busy)

    def ask(self):
        if self._busy:
            return  # מונע שליחה כפולה בזמן שהתשובה הקודמת עוד רצה
        q = self.inp.toPlainText().strip()
        if not q:
            return

        self.append_bubble(q, is_user=True)
        self.inp.clear()
        self.set_busy(True)

        # אינדיקציה "ה-AI חושב…"
        self._typing_lbl = QLabel("…ה-AI חושב")
        self._typing_lbl.setStyleSheet("color:#6b7280; padding:4px;")
        tip_line = QHBoxLayout()
        tip_line.addWidget(self._typing_lbl)
        tip_line.addStretch()
        self.chat_area.insertLayout(self.chat_area.count() - 1, tip_line)

        # בקשת הרשת ב־Thread כדי לא לחסום UI
        self._worker = _ChatWorker(self.p, self.recipe_id, q)
        self._worker.done.connect(self._on_answer)
        self._worker.fail.connect(self._on_error)
        self._worker.finished.connect(lambda: self.set_busy(False))
        self._worker.start()

    def _remove_typing(self):
        if self._typing_lbl:
            self._typing_lbl.setParent(None)
            self._typing_lbl = None

    def _on_answer(self, data: dict):
        self._remove_typing()
        ans = (data.get("answer") or "").strip() or "(לא התקבלה תשובה)"
        self.append_bubble(ans, is_user=False)

    def _on_error(self, msg: str):
        self._remove_typing()
        self.append_bubble(f"[שגיאה] {msg}", is_user=False)

    def clear_chat(self):
        # מוחק את כל הבועות ומשאיר את ה-stretch האחרון
        while self.chat_area.count() > 1:
            item = self.chat_area.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            lay = item.layout()
            if lay:
                while lay.count():
                    it = lay.takeAt(0)
                    ww = it.widget()
                    if ww:
                        ww.deleteLater()
