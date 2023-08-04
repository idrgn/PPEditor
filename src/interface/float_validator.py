from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator


class FloatValidator(QRegExpValidator):
    def __init__(self, min_value, max_value, parent=None):
        super(FloatValidator, self).__init__(
            QRegExp(r"^[+,-]?(\d+\.?\d*|\.\d+)$"), parent
        )
        self.minimum = min_value
        self.maximum = max_value

    def validate(self, input_str, pos):
        state, input_str, pos = super(FloatValidator, self).validate(input_str, pos)

        if state == QRegExpValidator.Acceptable:
            try:
                value = float(input_str)
            except ValueError as _:
                return QRegExpValidator.Invalid, input_str, pos
            if self.minimum is not None and value < self.minimum:
                return QRegExpValidator.Invalid, input_str, pos
            if self.maximum is not None and value > self.maximum:
                return QRegExpValidator.Invalid, input_str, pos

        return state, input_str, pos
