import typing

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QComboBox, QHeaderView, QListView, QTableView,
                             QWidget)

from param.param import Field


class PopulateThread(QThread):
    finished = pyqtSignal()

    def __init__(self, combo_box):
        super().__init__()
        self.combo_box = combo_box

    def run(self):
        self.combo_box.addItems(self.combo_box.field.settings.enum.get_values())
        self.finished.emit()


class QComboBoxField(QComboBox):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.populate_thread = PopulateThread(self)
        self.populate_thread.finished.connect(self.after_population)
        self.setDisabled(True)
        self.setView(QListView())

    def add_options(self, options: list):
        for i in range(len(options) - 1):
            self.addItem(f"{i} ({options[i]})")

    def set_field(self, field: Field):
        if field.settings.enum:
            self.field = field

            self.populate_thread.start()

    def after_population(self):
        self.currentTextChanged.connect(self.update_field_value)
        self.setDisabled(False)
        if self.field.settings.enum.null_value is not None:
            self.setCurrentIndex(self.field.value + 1)
        else:
            self.setCurrentIndex(self.field.value)

    def update_field_value(self, *args):
        if self.field is not None:
            index = self.currentIndex()
            if self.field.settings.enum.null_value is not None:
                self.field.set_value(index - 1)
            else:
                self.field.set_value(index)
