from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QDialog, QHBoxLayout, QStackedWidget
)
from components.app_header import AppHeader
from components.app_sidebar import AppSidebar
from views.search_page import SearchPage
from views.orders_page import OrdersPage
from views.chatbot_page import ChatbotPage
from views.recipe_page import RecipePage         # ← חדש: דף פרטי מתכון
from views.login_dialog import LoginDialog
from services.auth import AUTH
from PySide6.QtCore import Qt

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
        # נקה את ה־centralWidget כדי לא להשאיר תוכן מאחור
        old = self.takeCentralWidget()
        if old:
            old.deleteLater()

        # הסתר את החלון הראשי בזמן ההתחברות (ככה הוא לא "מבצבץ" מאחור)
        self.hide()

        # חלון התחברות גדול, ניתן להגדלה, ושומר על הסטייל הירוק הקיים
        dlg = LoginDialog(self)
        dlg.setWindowTitle('FoodGenius - כניסה למערכת')
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setSizeGripEnabled(True)
        dlg.setMinimumSize(900, 640)
        dlg.resize(1024, 720)

        # הוסף כפתורי מיזעור/הגדלה בחלון
        dlg.setWindowFlags(
            dlg.windowFlags()
            | Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )

        # מרכז למסך
        geom = self.screen().availableGeometry()
        dlg.move(geom.center() - dlg.rect().center())

        if dlg.exec() == QDialog.Accepted:
            self.show_main_content()
            self.show()  # החזרת החלון הראשי
        else:
            self.close()

    def show_main_content(self):
        # עטיפה כללית
        root = QWidget()
        root.setObjectName('Canvas')
        root_v = QVBoxLayout(root)
        root_v.setContentsMargins(16, 16, 16, 16)
        root_v.setSpacing(12)

        # כותרת עליונה
        header = AppHeader(self.handle_logout, AUTH.user)
        root_v.addWidget(header)

        # גוף: סיידבר + סטאק
        body = QWidget()
        body_h = QHBoxLayout(body)
        body_h.setContentsMargins(0, 0, 0, 0)
        body_h.setSpacing(12)

        self.sidebar = AppSidebar()
        body_h.addWidget(self.sidebar, 0)

        self.stack = QStackedWidget()

        # עמודים
        self.page_recipes = SearchPage(self, on_open=self.open_recipe)  # ← מעבירים callback
        self.page_orders  = OrdersPage(self)
        self.page_chat    = ChatbotPage(self)
        self.page_recipe  = RecipePage(self)                             # ← דף פרטי מתכון

        self.stack.addWidget(self.page_recipes)  # index 0
        self.stack.addWidget(self.page_orders)   # index 1
        self.stack.addWidget(self.page_chat)     # index 2
        self.stack.addWidget(self.page_recipe)   # index 3

        body_h.addWidget(self.stack, 1)
        root_v.addWidget(body, 1)
        self.setCentralWidget(root)

        # חיבורים
        self.sidebar.navigate.connect(self.on_nav)
        

        # חזרה מהרצף “פרטי מתכון” לרשימת מתכונים
        self.page_recipe.back_requested.connect(lambda: self.on_nav("recipes"))

        # ברירת מחדל
        self.on_nav("recipes")

    def on_nav(self, key: str):
        if key == "recipes":
            self.stack.setCurrentWidget(self.page_recipes)
        elif key == "orders":
            self.stack.setCurrentWidget(self.page_orders)
        elif key == "chatbot":
            self.stack.setCurrentWidget(self.page_chat)
        # כשנכנסים לעמוד פרטי מתכון דרך open_recipe לא צריך מקש בסיידבר,
        # אבל נשאיר את ההדגשה על “Recipes”
        self.sidebar.set_active(key if key in ("recipes", "orders", "chatbot") else "recipes")

    # ↓ זה ה-callback שמתקבל מכרטיס המתכון
    def open_recipe(self, rid: str):
        """נטען מתכון ונעבור למסך הפרטים בתוך אותו חלון"""
        self.page_recipe.load_recipe(rid)
        self.stack.setCurrentWidget(self.page_recipe)
        self.sidebar.set_active("recipes")  # משאיר את ההדגשה על 'Recipes'

    def handle_logout(self):
            # התנתקות נקייה: נקה את המרכז והצג שוב את מסך ההתחברות
            AUTH.clear_auth()
            old = self.takeCentralWidget()
            if old:
                old.deleteLater()
            self.show_login()
