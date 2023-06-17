import sys
import typing

from PyQt5 import QtGui
from PyQt5.QtWidgets import QCheckBox, QWidget

from param.param import Field


class QCheckBoxField(QCheckBox):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.stateChanged.connect(self.update_field_value)

    def set_field(self, field: Field):
        if field.settings.type == "bool":
            self.field = field
            self.setChecked(field.value)
            self.setToolTip(field.settings.description)

    def update_field_value(self, value: bool):
        try:
            self.field.set_value(value)
        except Exception as _:
            pass
