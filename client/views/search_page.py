# client/views/search_page.py
from typing import Callable, List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QGridLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from presenters.search_presenter import SearchPresenter
from components.recipe_card import RecipeCard
from views.recipe_page import RecipePage

class _SearchWorker(QThread):
    done = Signal(list)
    fail = Signal(str)

    def __init__(self, presenter: SearchPresenter, query: str):
        super().__init__()
        self.presenter = presenter
        self.query = query

    def run(self):
        try:
            results = self.presenter.search(self.query or "")
            self.done.emit(results or [])
        except Exception as e:
            self.fail.emit(str(e))


class SearchPage(QWidget):
    """דף חיפוש בתוך ה-stack. מקבל open_recipe_cb/on_open כדי לפתוח עמוד מתכון."""
    def __init__(self, open_recipe_cb: Callable[[str], None] | None = None,
                 p: QWidget | None = None, **kwargs):
        super().__init__(p)
        self.p = SearchPresenter(self)
        self._worker: _SearchWorker | None = None

        # תומך גם ב-on_open וגם ב-open_recipe_cb, עם עדיפות ל-on_open אם הוא callable
        cb_kw = kwargs.get("on_open")
        self._open_recipe_cb = cb_kw if callable(cb_kw) else (open_recipe_cb if callable(open_recipe_cb) else None)

        # 🔍 שורת חיפוש
        self.q = QLineEdit(placeholderText='חפשי: cake, chicken, rice…')
        self.btn = QPushButton('חיפוש'); self.btn.setProperty('accent', True)
        self.btn.setFixedHeight(40)

        # 🔝 שורת חיפוש + כפתור
        top = QHBoxLayout()
        top.addWidget(self.q, 1)
        top.addWidget(self.btn)

        # 🎛️ רשת תוצאות בתוך Scroll
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(14)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.wrap = QWidget()
        self.wrap.setLayout(self.grid)
        self.scroll.setWidget(self.wrap)

        # מצב טעינה / אין תוצאות
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("color:#6b7280; padding:6px;")
        self.status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 🧱 הרכבה
        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(self.status)
        root.addWidget(self.scroll, 1)

        # 🔁 חיבורים
        self.btn.clicked.connect(self.search)
        self.q.returnPressed.connect(self.search)

    # ---------- לוגיקה ----------
    def set_busy(self, busy: bool, msg: str = ""):
        self.btn.setEnabled(not busy if isinstance(busy, bool) else True)  # לא קריטי, להשקטת טייפינג
        self.btn.setEnabled(not busy)
        self.q.setEnabled(not busy)
        self.status.setText(msg if busy else "")

    def clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def paint_results(self, results: List[Dict]):
        self.clear_grid()
        if not results:
            self.status.setText("לא נמצאו תוצאות.")
            return
        self.status.setText("")
        for idx, r in enumerate(results):
            self.grid.addWidget(RecipeCard(r, self.open_recipe), idx // 3, idx % 3)
        # גלילה לראש
        self.scroll.verticalScrollBar().setValue(0)

    def open_recipe(self, rid: str):
        # אם יש callback מה־MainWindow – נשתמש בו; אחרת פולבאק לדיאלוג
        if callable(self._open_recipe_cb):
            self._open_recipe_cb(rid)
            return
        dlg = RecipePage(rid, self)
        dlg.exec()

    def search(self):
        query = self.q.text().strip()
        if self._worker and self._worker.isRunning():
            return  # מונע חיפוש כפול במקביל

        self.set_busy(True, "טוען תוצאות…")
        self._worker = _SearchWorker(self.p, query)
        self._worker.done.connect(lambda res: (self.set_busy(False), self.paint_results(res)))
        self._worker.fail.connect(lambda err: (self.set_busy(False), self.status.setText(f"שגיאה: {err}")))
        self._worker.start()
