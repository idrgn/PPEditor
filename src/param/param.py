from struct import pack

from const import PARAM_HEADER
from data import (
    read_byte_array,
    read_uint,
    replace_byte_array,
)

from settings.settings import Settings
from param.param_section import ParamSection
from param.param_entry import ParamEntry


class Param:
    """
    Param object
    """

    def __init__(self, data: bytes | None = b"", settings: Settings = None):
        self.is_modified = None
        self.entry_list = None
        self.section_list = None
        self.id = None
        self.unk3 = None
        self.unk2 = None
        self.sections_amount = None
        self.unk1 = None
        self.ptr = None
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
        Sets default values
        """

        # Header values
        self.ptr = None
        self.unk1 = None
        self.sections_amount = None
        self.unk2 = None
        self.unk3 = None
        self.id = None

        # Section list
        self.section_list: list[ParamSection] = []

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

        section_info_offset = 0x20
        data_offset = self.ptr

        for section_index in range(self.sections_amount):
            section_settings = self.settings.get_entries_in_param(
                self.id, section_index
            )

            section_entries_amount = read_uint(data, section_info_offset)
            entry_size = read_uint(data, section_info_offset + 0x4)
            raw_data = read_byte_array(
                data, data_offset, section_entries_amount * entry_size
            )

            self.section_list.append(
                ParamSection(
                    section_index,
                    section_settings,
                    entry_size,
                    section_entries_amount,
                    raw_data,
                )
            )

            section_info_offset += 0x8
            data_offset += len(raw_data)

    def get_section_entry_amount(self, section_index: int = 0) -> int | None:
        if section_index > len(self.section_list):
            return None
        else:
            return self.section_list[section_index].entry_amount

    def get_section_entries(self, section_index: int = 0) -> list[ParamEntry] | None:
        if section_index > len(self.section_list):
            return None
        else:
            return self.section_list[section_index].entry_list

    def get_section_entry(
        self, section_index: int = 0, entry_index: int = 0
    ) -> ParamEntry | None:
        if section_index > len(self.section_list):
            return None
        else:
            section = self.section_list[section_index]
            if entry_index > len(section.entry_list):
                return None
            else:
                return section.entry_list[entry_index]

    def get_section(self, section_index: int = 0) -> ParamSection | None:
        if section_index > len(self.section_list):
            return None
        else:
            return self.section_list[section_index]

    def add_section(self, size, entries_amount):
        self.section_list.append(
            ParamSection(
                len(self.section_list),
                None,
                size,
                entries_amount,
                b"\x00" * size * entries_amount,
            )
        )
        self.sections_amount += 1

    def is_changed(self) -> bool:
        return any((section.is_changed() for section in self.section_list))

    def to_bytes(self) -> bytes:
        # 0x0 - 0x4
        raw_data = PARAM_HEADER

        # 0x8 - 0xC - 0x10
        raw_data += pack(
            "III",
            self.ptr,
            self.unk1,
            self.sections_amount,
        )

        # 0x14 - 0x18 - 0x1C
        raw_data += pack(
            "III",
            self.unk2,
            self.id,
            self.unk3,
        )

        section_contents = b""

        # Write section info and append content
        for section in self.section_list:
            raw_data += pack("II", section.entry_amount, section.entry_size)
            section_contents += section.to_bytes()

        # Fill with zeroes
        if len(raw_data) % 0x10 != 0:
            raw_data += b"\x00" * (len(raw_data) % 0x10)

        # Overwrite base pointer with starting position of data
        raw_data = replace_byte_array(raw_data, 0x8, pack("I", len(raw_data)))

        # Append section content
        raw_data += section_contents

        return raw_data
