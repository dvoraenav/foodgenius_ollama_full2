import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    theme_path = os.path.join(os.path.dirname(__file__), "assets", "theme.qss")
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as f: 
            app.setStyleSheet(f.read())
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()