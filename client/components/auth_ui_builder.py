from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class AuthUIBuilder:
    def show_error_message(self, label: QLabel, message: str):
        label.setText(message)
        label.setStyleSheet("color: red")
        label.show()

    def show_success_message(self, label: QLabel, message: str):
        label.setText(message)
        label.setStyleSheet("color: green")
        label.show()

    def clear_messages(self, *labels: QLabel):
        for label in labels:
            label.clear()
            label.hide()

