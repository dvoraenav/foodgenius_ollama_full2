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
        
        # Check if user is already logged in
        if AUTH.is_authenticated():
            self.show_main_content()
        else:
            self.show_login()
    
    def show_login(self):
        """Show login dialog and wait for successful login"""
        login_dialog = LoginDialog(self)
        login_dialog.setWindowTitle('FoodGenius - כניסה למערכת')
        
        # Make dialog modal and show it
        if login_dialog.exec() == QDialog.Accepted:
            # Login successful, show main content
            self.show_main_content()
        else:
            # User cancelled login, close application
            self.close()
    
    def show_main_content(self):
        """Show the main application content after successful login"""
        # Create main content widget
        canvas = QWidget()
        canvas.setObjectName('Canvas')
        
        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Add header with user info and logout option
        header = AppHeader(self.handle_logout, AUTH.user)
        layout.addWidget(header)
        
        # Add search page
        search_page = SearchPage(self)
        layout.addWidget(search_page, 1)
        
        # Set as central widget
        self.setCentralWidget(canvas)
    
    def handle_logout(self):
        """Handle user logout - close main window and show login"""
        # Clear authentication
        AUTH.clear_auth()
        
        # Hide the main window
        self.hide()
        
        # Show login dialog as standalone window
        login_dialog = LoginDialog()
        login_dialog.setWindowTitle('FoodGenius - כניסה למערכת')
        
        if login_dialog.exec() == QDialog.Accepted:
            # Login successful, show main content again
            self.show_main_content()
            self.show()
        else:
            # User cancelled login, close application
            self.close()
    
    def open_login(self):
        """Legacy method - now handled in __init__"""
        pass