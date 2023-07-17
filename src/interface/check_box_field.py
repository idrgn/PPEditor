import typing

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QWidget

from src.param.param_field import ParamField


class QCheckBoxField(QCheckBox):
    field_changed = pyqtSignal(ParamField)

    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.stateChanged.connect(self.update_field_value)

    def set_field(self, field: ParamField):
        if field.settings.type == "bool":
            self.field = field
            self.setChecked(field.value)
            self.setToolTip(field.settings.description)

    def update_field_value(self, value: bool):
        try:
            self.field.set_value(value)
            self.field_changed.emit(self.field)
        except Exception as _:
            pass
