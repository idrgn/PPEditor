from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class WarningWindow(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.message_label = QLabel(message)
        self.ok_button = QPushButton("OK")

        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
