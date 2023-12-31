import typing

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QLineEdit, QWidget

from data import color_to_int, int_to_color
from param.param_field import ParamField


class QColorPickerField(QLineEdit):
    field_changed = pyqtSignal(ParamField)
    clicked = pyqtSignal()

    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.color = None
        self.setReadOnly(True)
        self.setText("No color selected")
        self.clicked.connect(self.get_new_color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        else:
            super().mousePressEvent(event)

    def set_field(self, field: ParamField):
        if field.settings.type == "rgba":
            self.field = field
            self.color = field.value
            self.update_aspect()

    def update_field_value(self, value: bool):
        try:
            self.field.set_value(value)
            self.field_changed.emit(self.field)
        except Exception as _:
            pass

    def get_new_color(self):
        if self.color is None:
            base_color = QColor(255, 255, 255, 255)
        else:
            red, green, blue, alpha = int_to_color(self.color)
            base_color = QColor(red, green, blue, alpha)

        color = QColorDialog.getColor(
            base_color, self, "Select Color", options=QColorDialog.ShowAlphaChannel
        )

        if color.isValid():
            new_color = color_to_int(color.getRgb())
            self.field.set_value(new_color)
            self.field_changed.emit(self.field)
            self.color = new_color
            self.update_aspect()

    def update_aspect(self):
        red, green, blue, alpha = int_to_color(self.color)
        self.setStyleSheet(
            f"QLineEdit {{ background: rgba({red:f}, {green:f}, {blue:f}, {alpha:f});}}"
        )
        self.setText(f"rgba({red}, {green}, {blue}, {alpha})")
