import typing

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QComboBox, QHeaderView, QListView, QTableView, QWidget

from param.param import Field


class QComboBoxField(QComboBox):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.setDisabled(True)
        self.setView(QListView())

    def add_options(self, options: list):
        for i in range(len(options) - 1):
            self.addItem(f"{i} ({options[i]})")

    def set_field(self, field: Field):
        if field.settings.enum:
            self.field = field
            self.addItems(field.settings.enum.get_values())
            self.setDisabled(False)
            if self.field.settings.enum.null_value is not None:
                self.setCurrentIndex(self.field.value + 1)
            else:
                self.setCurrentIndex(self.field.value)
            self.currentTextChanged.connect(self.update_field_value)

    def update_field_value(self, *args):
        if self.field is not None:
            index = self.currentIndex()
            if self.field.settings.enum.null_value is not None:
                self.field.set_value(index - 1)
            else:
                self.field.set_value(index)
