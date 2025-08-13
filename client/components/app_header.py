from PySide6.QtWidgets import QFrame,QHBoxLayout,QLabel,QPushButton
class AppHeader(QFrame):
    def __init__(self,on_login):
        super().__init__(); self.setObjectName('Header')
        h=QHBoxLayout(self); h.setContentsMargins(16,12,16,12)
        t=QLabel('FoodGenius — מצאי מתכונים לפי חומרים'); t.setStyleSheet('font-weight:700; color:white; font-size:16px;')
        b=QPushButton('כניסה / הרשמה'); b.setProperty('accent', True); b.clicked.connect(on_login)
        h.addWidget(t); h.addStretch(1); h.addWidget(b)
