from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDialog
from components.app_header import AppHeader
from views.search_page import SearchPage
from views.login_dialog import LoginDialog
from services.auth import AUTH

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FoodGenius')
        self.setMinimumSize(1120, 760)

        if AUTH.is_authenticated():
            self.show_main_content()
        else:
            self.show_login()

    def show_login(self):
        login_dialog = LoginDialog(self)
        login_dialog.setWindowTitle('FoodGenius - כניסה למערכת')

        if login_dialog.exec() == QDialog.Accepted:
            self.show_main_content()
        else:
            self.close()

    def show_main_content(self):
        canvas = QWidget()
        canvas.setObjectName('Canvas')

        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = AppHeader(self.handle_logout, AUTH.user)
        layout.addWidget(header)

        search_page = SearchPage(self)
        layout.addWidget(search_page, 1)

        self.setCentralWidget(canvas)

    def handle_logout(self):
        AUTH.clear_auth()
        self.show_login()
