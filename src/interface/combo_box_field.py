import typing

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QListView,
    QListWidget,
    QVBoxLayout,
    QWidget,
)

from param.param_field import ParamField


class QComboBoxField(QComboBox):
    field_changed = pyqtSignal(ParamField)

    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.field = None
        self.is_long = False
        self.setDisabled(True)
        self.setView(QListView())

    def set_field(self, field: ParamField):
        if field.settings.enum:
            self.field = field
            entry_count = len(field.settings.enum.get_values())
            if entry_count > 50:
                self.set_values_long()
            else:
                self.set_values_short()
            self.setDisabled(False)

    def set_values_short(self):
        self.addItems(self.field.settings.enum.get_values())
        if self.field.settings.enum.null_value is not None:
            self.setCurrentIndex(self.field.value + 1)
        else:
            self.setCurrentIndex(self.field.value)
        self.currentTextChanged.connect(self.update_field_value)

    def set_values_long(self):
        index = self.field.value
        if self.field.settings.enum.null_value is not None:
            index += 1
        self.addItem(self.field.settings.enum.get_values()[index])
        self.is_long = True

    def update_field_value(self, *args):
        if self.field is not None:
            index = self.currentIndex()
            if self.field.settings.enum.null_value is not None:
                self.field.set_value(index - 1)
            else:
                self.field.set_value(index)
            self.field_changed.emit(self.field)

    def showPopup(self) -> None:
        if not self.is_long:
            return super().showPopup()

        index = self.field.value

        if self.field.settings.enum.null_value is not None:
            index += 1

        list_dialog = ListDialog(self.field.settings.enum.get_values(), index)
        if list_dialog.exec_() == QDialog.Accepted:
            selected_item, selected_index = list_dialog.get_selected_item()
            if selected_item is None and selected_index == -1:
                return
            self.setItemText(0, selected_item)
            if self.field.settings.enum.null_value is not None:
                self.field.set_value(selected_index - 1)
            else:
                self.field.set_value(selected_index)
            self.field_changed.emit(self.field)


class ListDialog(QDialog):
    def __init__(self, items: list, selected: int = 0):
        super().__init__()
        self.setWindowTitle("Select an entry")

        # List
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(items)
        self.list_widget.itemDoubleClicked.connect(self.accept)
        self.list_widget.setCurrentRow(selected)

        # Buttons
        button_box = QDialogButtonBox()
        select_button = button_box.addButton("Select", QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        select_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_selected_item(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0].text()
            selected_index = self.list_widget.row(selected_items[0])
            return selected_item, selected_index
        else:
            return None, -1
