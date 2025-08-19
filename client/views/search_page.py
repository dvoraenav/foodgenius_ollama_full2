from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QGridLayout
)
from presenters.search_presenter import SearchPresenter
from components.recipe_card import RecipeCard
from views.recipe_view import RecipeView

class SearchPage(QWidget):
    def __init__(self, p=None):
        super().__init__(p)
        self.p = SearchPresenter(self)

        # 🔍 שורת חיפוש
        self.q = QLineEdit(placeholderText='חפשי: cake, chicken, rice…')
        self.btn = QPushButton('חיפוש')
        self.btn.setProperty('accent', True)

        # 🔝 שורת חיפוש + כפתור
        top = QHBoxLayout()
        top.addWidget(self.q, 1)
        top.addWidget(self.btn)

        # 🎛️ רשת תוצאות
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        wrap = QWidget()
        wrap.setLayout(self.grid)
        scroll.setWidget(wrap)

        # 🧱 הרכבה
        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(scroll, 1)

        # 🔁 חיבורים
        self.btn.clicked.connect(self.search)
        self.q.returnPressed.connect(self.search)

    def search(self):
        query = self.q.text().strip()
        res = self.p.search(query)

        # ניקוי הרשת
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:
                w.deleteLater()

        # הצגת תוצאות
        for idx, r in enumerate(res):
            self.grid.addWidget(RecipeCard(r, self.open_recipe), idx // 3, idx % 3)

    def open_recipe(self, rid: str):
        dlg = RecipeView(rid, self)
        dlg.exec()
