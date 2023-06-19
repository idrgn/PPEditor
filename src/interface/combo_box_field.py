import typing

from PyQt5.QtWidgets import QComboBox, QWidget

from param.param import Field


class QComboBoxField(QComboBox):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None

    def add_options(self, options: list):
        for i in range(len(options) - 1):
            self.addItem(f"{i} ({options[i]})")

    def set_field(self, field: Field):
        if field.settings.enum:
            self.field = field
            self.addItems(field.settings.enum.get_values())
            self.setCurrentIndex(field.value + 1)
            self.currentTextChanged.connect(self.update_field_value)

    def update_field_value(self, *args):
        if self.field is not None:
            index = self.currentIndex()
            self.field.set_value(index - 1)
