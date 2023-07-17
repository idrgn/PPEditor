import os
import shutil
import sys

from PyQt5 import QtGui, QtWidgets

from data import bytes_to_string, resource_path, string_to_bytes, validate_byte_string
from interface import main_window
from interface.check_box_field import QCheckBoxField
from interface.color_picker_field import QColorPickerField
from interface.combo_box_field import QComboBoxField
from interface.line_edit_field import QLineEditField
from param.param import Param
from settings.settings import Settings


class Application(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_connections()
        self.setWindowIcon(QtGui.QIcon(str(resource_path("res/icon.png"))))

        # Load settings from settings file
        self.settings = Settings()

        # Add the enums from msg files
        directory = resource_path("res/msg/")
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            with open(resource_path(f), "rb") as file:
                data = file.read()
                self.settings.add_enum_from_msg(os.path.splitext(filename)[0], data)

        # Load other data
        data = open(resource_path("res/settings.txt")).readlines()
        self.settings.load_enums_from_data(data)
        self.settings.load_fields_from_data(data)

        # Create param file
        self.param = Param(None, self.settings)
        self.path = None

        # If opened via cmd with parameters
        if len(sys.argv) > 1:
            if sys.argv[1]:
                file = sys.argv[1]
                file = file.replace("\\", "/")
                self.load_param_file(file)

    def set_connections(self):
        """
        Set UI element connections
        """
        self.action_load.triggered.connect(self.select_param)
        self.action_save.triggered.connect(self.save_param_file)
        self.action_refresh.triggered.connect(self.refresh)
        self.cb_sections.currentTextChanged.connect(self.selected_section_changed)
        self.cb_entries.currentTextChanged.connect(self.selected_entry_changed)
        self.pb_copy_entry.clicked.connect(self.copy_entry)
        self.pb_paste_entry.clicked.connect(self.paste_entry)
        self.pb_remove_current_entry.clicked.connect(self.remove_entry)
        self.pb_add_new_emtry.clicked.connect(self.add_entry)

    def select_param(self):
        """
        Opens select param
        """
        input_file = QtWidgets.QFileDialog.getOpenFileName(self, "Open")
        if input_file:
            if input_file[0] != "":
                self.load_param_file(input_file[0])

    def load_param_file(self, file):
        """
        Read Param file
        """
        with open(file, "r+b") as f:
            data = f.read()
            self.path = file
            self.param.load_from_data(data)
            self.output_path = os.path.dirname(os.path.abspath(self.path))
            self.file_name = os.path.basename(os.path.abspath(self.path))
            self.lb_file_name.setText(f"Filename: {self.file_name}")
            self.refresh()

    def save_param_file(self):
        """
        Saves Param file
        """

        # Save backup if enabled in settings
        if self.check_backup.isChecked:
            shutil.copy(self.path, f"{self.path}.bak")

        # Save file
        if self.path and self.param:
            data_to_save = self.param.to_bytes()
            with open(self.path, "wb") as f:
                f.write(data_to_save)

    def refresh(self):
        """
        Refreshes UI
        """
        if self.param is None:
            return

        self.load_sections()
        self.load_entries()

    def selected_section_changed(self):
        """
        Loads entry list of selected section
        """
        self.load_entries()

    def load_sections(self):
        """
        Loads sections
        """
        self.cb_sections.clear()
        for section in self.param.section_list:
            self.cb_sections.addItem(f"{section.id+1} ({section.entry_amount} entries)")

    def load_entries(self):
        """
        Loads entries
        """
        self.cb_entries.clear()
        for entry in self.param.get_section_entries(self.cb_sections.currentIndex()):
            entry_name = entry.get_name()
            if entry_name == "":
                self.cb_entries.addItem(f"{entry.id}")

            else:
                self.cb_entries.addItem(f"{entry.id}: {entry_name}")

    def selected_entry_changed(self):
        """
        Loads field list of current entry
        """
        scroll_position = self.sc.verticalScrollBar().value()
        self.sc.setVisible(False)
        self.clear_form_items()

        current_section = self.cb_sections.currentIndex()
        current_entry = self.cb_entries.currentIndex()

        for field in self.param.get_section_entry(
            current_section, current_entry
        ).fields:
            label = QtWidgets.QLabel(field.settings.name)
            label.setToolTip(field.settings.description)

            if field.settings.type == "bool":
                widget = QCheckBoxField(self.sc_content)
            elif (
                field.settings.enum
                and field.value >= -1
                and field.value < len(field.settings.enum.get_values()) - 1
            ):
                widget = QComboBoxField(self.frame_controls)
            elif field.settings.type == "rgba":
                widget = QColorPickerField(self.sc_content)
            else:
                widget = QLineEditField(self.sc_content)
            widget.set_field(field)
            self.fl_fields.addRow(label, widget)

        self.sc.verticalScrollBar().setValue(scroll_position)
        self.sc.setVisible(True)

    def clear_form_items(self):
        """
        Clears all items in form
        """
        for i in reversed(range(self.fl_fields.count())):
            self.fl_fields.itemAt(i).widget().setParent(None)

    def get_current_entry(self):
        """
        Returns current selected entry
        """
        current_section_index = self.cb_sections.currentIndex()
        current_entry_index = self.cb_entries.currentIndex()

        current_entry = self.param.get_section_entry(
            current_section_index, current_entry_index
        )

        return current_entry

    def get_current_section(self):
        """
        Returns current selected section
        """
        current_section_index = self.cb_sections.currentIndex()
        current_section = self.param.get_section(current_section_index)
        return current_section

    def copy_entry(self):
        """
        Copies current entry in hex format
        """
        if self.param != None:
            current_section_index = self.cb_sections.currentIndex()
            current_entry_index = self.cb_entries.currentIndex()

            current_entry = self.param.get_section_entry(
                current_section_index, current_entry_index
            )

            text = bytes_to_string(current_entry.to_bytes())

            cb = QtWidgets.QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(text, mode=cb.Clipboard)

    def paste_entry(self):
        """
        Pastes current entry in hex format
        """
        cb = QtWidgets.QApplication.clipboard()
        text = cb.text()
        if validate_byte_string(text):
            ba = string_to_bytes(text)

            current_section_index = self.cb_sections.currentIndex()
            current_entry_index = self.cb_entries.currentIndex()

            current_entry = self.param.get_section_entry(
                current_section_index, current_entry_index
            )

            current_entry.raw_data = ba
            current_entry.process_data()
            self.selected_entry_changed()

    def remove_entry(self):
        """
        Removes current entry
        """
        current_section_index = self.cb_sections.currentIndex()
        current_entry_index = self.cb_entries.currentIndex()

        current_entry = self.param.get_section_entry(
            current_section_index, current_entry_index
        )

        current_section = self.param.get_section(current_section_index)
        current_section.remove_entry(current_entry)

        self.cb_entries.removeItem(current_entry_index)

    def add_entry(self):
        """ """
        current_section = self.get_current_section()
        current_section.add_entry()
        self.load_entries()
