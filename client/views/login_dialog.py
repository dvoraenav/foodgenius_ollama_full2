from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLineEdit,QPushButton,QMessageBox
from presenters.auth_presenter import AuthPresenter
class LoginDialog(QDialog):
    def __init__(self,p=None):
        super().__init__(p); self.p=AuthPresenter(self); self.setWindowTitle('כניסה / הרשמה'); self.setMinimumWidth(380)
        self.email=QLineEdit(placeholderText='אימייל'); self.name=QLineEdit(placeholderText='שם (לרישום)'); self.pw=QLineEdit(placeholderText='סיסמה'); self.pw.setEchoMode(QLineEdit.Password)
        self.b1=QPushButton('כניסה'); self.b2=QPushButton('הרשמה')
        lay=QVBoxLayout(self); lay.addWidget(self.email); lay.addWidget(self.name); lay.addWidget(self.pw)
        row=QHBoxLayout(); row.addWidget(self.b1); row.addWidget(self.b2); lay.addLayout(row)
        self.b1.clicked.connect(self._login); self.b2.clicked.connect(self._register)
    def _login(self):
        try:
            self.p.login(self.email.text().strip(), self.pw.text().strip()); self.accept()
        except Exception as e:
            QMessageBox.critical(self,'שגיאה',str(e))
    def _register(self):
        try:
            self.p.register(self.email.text().strip(), self.name.text().strip(), self.pw.text().strip())
            QMessageBox.information(self,'הצלחה','נרשמת! עכשיו התחברי.')
        except Exception as e:
            QMessageBox.critical(self,'שגיאה',str(e))
