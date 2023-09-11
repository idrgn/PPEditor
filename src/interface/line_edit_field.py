import typing

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QWidget

from interface.float_validator import FloatValidator
from param.param_field import ParamField


class QLineEditField(QLineEdit):
    field_changed = pyqtSignal(ParamField)

    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.original_value = None

    def set_field(self, field: ParamField):
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
        elif type == "ushort":
            validator.setRange(0, 65535)
        elif type == "short":
            validator.setRange(-32767 - 1, 32767)
        elif type == "uchar":
            validator.setRange(0, 255)
        elif type == "char":
            validator.setRange(-127 - 1, 127)
        elif type == "bool":
            validator.setRange(0, 1)
        elif type == "float":
            validator = FloatValidator(-3.4028235e38, 3.4028235e38)
        elif type == "str" or type == "string":
            validator = None
            self.setMaxLength(size - 1)
        else:
            validator = None

        if validator is not None:
            self.setValidator(validator)

    def update_field_value(self, value: str):
        try:
            self.field.set_value_from_string(value)
            self.field_changed.emit(self.field)
        except Exception as e:
            print(f"Error when setting field value: {e}")
