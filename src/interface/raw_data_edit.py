from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QTextEdit, QVBoxLayout

from src.data import validate_byte_string


class RawDataEditWindow(QDialog):
    def __init__(self, parent=None, text: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Editing Raw Data")

        self.text_edit = QTextEdit()
        self.text_edit.setText(text)
        self.text_edit.textChanged.connect(self.text_changed)

        self.format_label = QLabel()
        self.format_label.setAlignment(Qt.AlignCenter)
        self.format_label.setStyleSheet("color: red;")

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_text)
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.format_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def save_text(self):
        text = self.text_edit.toPlainText()
        if validate_byte_string(text):
            self.accept()

    def text_changed(self):
        text = self.text_edit.toPlainText()
        if validate_byte_string(text):
            self.format_label.setText("")
            self.save_button.setEnabled(True)
        else:
            self.format_label.setText("Incorrect format")
            self.save_button.setEnabled(False)
