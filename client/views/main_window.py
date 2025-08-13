from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout
from components.app_header import AppHeader
from views.search_page import SearchPage
from views.login_dialog import LoginDialog
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('FoodGenius'); self.setMinimumSize(1120,760)
        canvas=QWidget(); canvas.setObjectName('Canvas'); v=QVBoxLayout(canvas); v.setContentsMargins(16,16,16,16); v.setSpacing(12)
        v.addWidget(AppHeader(self.open_login)); v.addWidget(SearchPage(self),1); self.setCentralWidget(canvas)
    def open_login(self): LoginDialog(self).exec()
