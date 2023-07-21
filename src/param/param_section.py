from data import (
    read_byte_array,
)

from param.param_entry import ParamEntry


class ParamSection:
    """
    Section object
    """

    def __init__(
        self,
        param_id: int,
        settings: list | None,
        entry_size: int,
        entry_amount: int,
        data: bytes,
    ):
        # Values
        self.id = param_id
        self.settings = settings
        self.entry_size = entry_size
        self.entry_amount = entry_amount

        # Entry list
        self.raw_data = data
        self.entry_list: list[ParamEntry] = []
        self._parse_data(data)

    def _parse_data(self, data):
        for index in range(self.entry_amount):
            raw_data = read_byte_array(data, index * self.entry_size, self.entry_size)
            self.entry_list.append(ParamEntry(index, self.settings, raw_data))

    def to_bytes(self) -> bytes:
        return b"".join((entry.to_bytes() for entry in self.entry_list))

    def remove_entry(self, entry: ParamEntry):
        self.entry_list.remove(entry)
        self.update_entry_amount()

    def add_entry(self, data: bytes = None):
        if data is None:
            data = b"\x00" * self.entry_size
        self.entry_list.append(ParamEntry(len(self.entry_list), self.settings, data))
        self.update_entry_amount()

    def update_entry_amount(self):
        self.entry_amount = len(self.entry_list)

    def is_changed(self) -> bool:
        return any((entry.is_changed() for entry in self.entry_list))
