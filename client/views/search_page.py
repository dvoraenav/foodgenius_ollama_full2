from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QPushButton,QScrollArea,QWidget,QGridLayout
from presenters.search_presenter import SearchPresenter
from components.recipe_card import RecipeCard
from views.recipe_view import RecipeView
class SearchPage(QWidget):
    def __init__(self,p=None):
        super().__init__(p); self.p=SearchPresenter(self)
        self.q=QLineEdit(placeholderText='חפשי חומרים: בטטה, קינואה…'); self.btn=QPushButton('חיפוש'); self.btn.setProperty('accent', True)
        top=QHBoxLayout(); top.addWidget(self.q,1); top.addWidget(self.btn)
        self.grid=QGridLayout(); self.grid.setHorizontalSpacing(14); self.grid.setVerticalSpacing(14)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); wrap=QWidget(); wrap.setLayout(self.grid); scroll.setWidget(wrap)
        root=QVBoxLayout(self); root.addLayout(top); root.addWidget(scroll,1)
        self.btn.clicked.connect(self.search); self.q.returnPressed.connect(self.search)
    def search(self):
        res=self.p.search(self.q.text().strip())
        while self.grid.count():
            w=self.grid.takeAt(0).widget();
            if w: w.deleteLater()
        for idx,r in enumerate(res):
            self.grid.addWidget(RecipeCard(r, self.open_recipe), idx//3, idx%3)
    def open_recipe(self,rid:str):
        dlg=RecipeView(rid,self); dlg.exec()
