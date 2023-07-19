from src.data import parse_bool, parse_int, read_int, read_str_short


class SettingsEnumEntry:
    def __init__(
        self, name: str, description: str, values: list, null_value: str = None
    ) -> None:
        self.name = name
        self.description = description
        self.values = values
        self.null_value = null_value

    def get_values(self):
        if self.null_value is not None:
            return [self.null_value] + self.values
        else:
            return self.values

    def get_value(self, index: int):
        if index == -1:
            return self.null_value
        else:
            if index >= len(self.values):
                return "Unknown"
            else:
                return self.values[index]


class SettingsFieldEntry:
    def __init__(
        self,
        id: int,
        section: int,
        addresss: int,
        size: int,
        name: str,
        description: str,
        type: str,
        shown: bool = False,
        enum: SettingsEnumEntry = None,
    ) -> None:
        self.id = id
        self.section = section
        self.address = addresss
        self.size = size
        self.name = name
        self.description = description
        self.type = type
        self.shown = shown
        self.enum = enum


class Settings:
    def __init__(self, data: list = []) -> None:
        self.enum_entries = []
        self.field_entries = []

        self.load_enums_from_data(data)
        self.load_fields_from_data(data)

    def load_fields_from_data(self, data: list) -> None:
        for line in data:
            if line.startswith("#") or line.startswith("E") or line.strip() == "":
                continue

            row_entries = line.split(";")

            for _ in range(10 - len(row_entries)):
                row_entries.append("")

            (
                id,
                section,
                address,
                size,
                name,
                description,
                type,
                shown,
                has_enum,
                enum_name,
            ) = [e.strip() for e in row_entries]

            id = int(id)

            if section != "*":
                section = int(section)

            address = parse_int(address)
            size = parse_int(size)
            description = bytes(description, "utf-8").decode("unicode_escape")
            shown = parse_bool(shown)
            has_enum = parse_bool(has_enum)

            if has_enum:
                enum = self.get_enum(enum_name)
            else:
                enum = None

            self.field_entries.append(
                SettingsFieldEntry(
                    id,
                    section,
                    address,
                    size,
                    name,
                    description,
                    type,
                    shown,
                    enum,
                )
            )

    def load_enums_from_data(self, data: list) -> None:
        for line in data:
            if not line.startswith("E"):
                continue

            enum = [e.strip() for e in line.split(";")]

            name, description, null_value = enum[1:4]
            values = enum[4:]

            self.add_enum(name, description, values, null_value)

    def get_entries_in_param(self, param_id: int, section: int = None) -> list:
        if section is not None:
            return [
                entry
                for entry in self.field_entries
                if (
                    entry.id == param_id
                    and (entry.section == section or entry.section == "*")
                )
            ]
        else:
            return [entry for entry in self.field_entries if entry.id == param_id]

    def get_enum(self, enum_name: str) -> SettingsEnumEntry:
        return [enum for enum in self.enum_entries if enum.name == enum_name][0]

    def add_enum(self, name, description, values, null_value: str = None):
        self.enum_entries.append(
            SettingsEnumEntry(name, description, values, null_value)
        )

    def add_enum_from_msg(self, name, data):
        values = []

        entry_amount = read_int(data, 0x0)

        for i in range(entry_amount):
            entry_index = read_int(data, 0x8 + i * 4)
            entry_message = read_str_short(data, entry_index)
            values.append(entry_message)

        self.enum_entries.append(SettingsEnumEntry(f"msg_{name}", None, values, None))
