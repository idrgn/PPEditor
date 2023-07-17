from struct import pack

from src.const import PARAM_HEADER
from src.data import (
    read_byte_array,
    read_uint,
    replace_byte_array,
)

from src.settings.settings import Settings
from src.param.param_section import ParamSection


class Param:
    """
    Param object
    """

    def __init__(self, data: bytes = b"", settings: Settings = None):
        self.settings = settings
        self.set_default_values()

        # Return if data file is not valid
        if (
            data is None
            or data == b""
            or read_byte_array(data, 0x0, 0x8) != PARAM_HEADER
        ):
            return

        # Load data from header
        self._parse_header(data)

        # Load all entry data
        self._process_data(data)

    def load_from_data(self, data: bytes = b""):
        """
        Loads from data
        Args:
            data (bytes, optional): _description_. Defaults to b"".
        """

        # Return if data file is not valid
        if data == b"" or read_byte_array(data, 0x0, 0x8) != PARAM_HEADER:
            return

        self.set_default_values()

        # Load data from header
        self._parse_header(data)

        # Load all entry data
        self._process_data(data)

    def set_default_values(self):
        """
        Sets default valyes
        """

        # Header values
        self.ptr = None
        self.unk1 = None
        self.sections_amount = None
        self.unk2 = None
        self.unk3 = None
        self.id = None

        # Section list
        self.section_list = []

        # Other
        self.entry_list = []
        self.is_modified = False

    def _parse_header(self, data: bytes):
        """
        Get initial values from the file header
        Args:
            data (bytes): File data
        """

        self.ptr = read_uint(data, 0x8)
        self.unk1 = read_uint(data, 0xC)
        self.sections_amount = read_uint(data, 0x10)
        self.unk2 = read_uint(data, 0x14)
        self.id = read_uint(data, 0x18)
        self.unk3 = read_uint(data, 0x1C)

    def _process_data(self, data: bytes):
        """
        Parses data from file header
        Args:
            data (bytes): raw file data
        """
        self.raw_data = data

        section_index = 0x20
        data_offset = self.ptr

        for section in range(self.sections_amount):
            section_settings = self.settings.get_entries_in_param(self.id, section)

            section_entries = read_uint(data, section_index)
            section_size = read_uint(data, section_index + 0x4)
            raw_data = read_byte_array(data, data_offset, section_entries * section_size)

            self.section_list.append(
                ParamSection(
                    section, section_settings, section_size, section_entries, raw_data
                )
            )

            section_index += 0x8
            data_offset += len(raw_data)

    def get_section_entry_amount(self, section_index: int = 0) -> int:
        if section_index > len(self.section_list):
            return None
        else:
            return self.section_list[section_index].entry_amount

    def get_section_entries(self, section_index: int = 0) -> int:
        if section_index > len(self.section_list):
            return None
        else:
            return self.section_list[section_index].entry_list

    def get_section_entry(self, section_index: int = 0, entry_index: int = 0):
        if section_index > len(self.section_list):
            return None
        else:
            section = self.section_list[section_index]
            if entry_index > len(section.entry_list):
                return None
            else:
                return section.entry_list[entry_index]

    def get_section(self, section_index: int = 0):
        if section_index > len(self.section_list):
            return None
        else:
            return self.section_list[section_index]

    def add_section(self, size, entries):
        self.section_list.append(
            ParamSection(
                len(self.section_list), None, size, entries, b"\x00" * size * entries
            )
        )
        self.sections_amount += 1

    def is_changed(self):
        for section in self.section_list:
            if section.is_changed():
                return True

        return False

    def to_bytes(self) -> bytes:
        # 0x0 - 0x4
        file = PARAM_HEADER

        # 0x8 - 0xC - 0x10
        file += pack(
            "III",
            self.ptr,
            self.unk1,
            self.sections_amount,
        )

        # 0x14 - 0x18 - 0x1C
        file += pack(
            "III",
            self.unk2,
            self.id,
            self.unk3,
        )

        section_contents = b""

        # Write section info and append content
        for section in self.section_list:
            file += pack("II", section.entry_amount, section.entry_size)
            section_contents += section.to_bytes()

        # Fill with zeroes
        if len(file) % 0x10 != 0:
            file += b"\x00" * (len(file) % 0x10)

        # Overwrite base pointer with starting position of data
        file = replace_byte_array(file, 0x8, pack("I", len(file)))

        # Append section content
        file += section_contents

        return file
