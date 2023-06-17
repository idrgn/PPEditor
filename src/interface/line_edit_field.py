import sys
import typing

from PyQt5 import QtGui
from PyQt5.QtWidgets import QLineEdit, QWidget

from param.param import Field


class QLineEditField(QLineEdit):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None

    def set_field(self, field: Field):
        self.field = field
        self.set_validator(field.settings.type, field.settings.size)
        self.setText(str(field.value))
        self.original_value = field.value
        self.textChanged.connect(self.update_field_value)

    def set_validator(self, type: str, size: int):
        validator = QtGui.QIntValidator()
        if type == "uint":
            validator.setRange(0, 4294967295)
        elif type == "int":
            validator.setRange(-2147483647 - 1, 2147483647)
        elif type == "short":
            validator.setRange(0, 65535)
        elif type == "ushort":
            validator.setRange(-32767 - 1, 32767)
        elif type == "char":
            validator.setRange(0, 255)
        elif type == "uchar":
            validator.setRange(-127 - 1, 127)
        elif type == "bool":
            validator.setRange(0, 1)
        elif type == "float":
            validator = QtGui.QDoubleValidator()
            validator.setRange(sys.float_info.min, sys.float_info.max)
        elif type == "str" or type == "string":
            validator = None
            self.setMaxLength(size - 1)

        if validator is not None:
            self.setValidator(validator)

    def update_field_value(self, value: str):
        self.field.set_value_from_string(value)
