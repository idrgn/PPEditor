import sys
import typing

from PyQt5 import QtGui
from PyQt5.QtWidgets import QComboBox, QWidget

from param.param import Field


class QComboBoxField(QComboBox):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.currentTextChanged.connect(self.update_field_value)

    def add_options(self, options: list):
        count = -1
        for option in options:
            self.addItem(f"{count} ({option})")
            count += 1

    def set_field(self, field: Field):
        if field.settings.type == "enum":
            self.field = field
            self.setCurrentIndex(field.value + 1)

    def update_field_value(self, *args):
        if self.field is not None:
            index = self.currentIndex()
            self.field.set_value(index - 1)
