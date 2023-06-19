from data import parse_bool, parse_int


class SettingsEnumEntry:
    def __init__(
        self, type: str, name: str, description: str, null_value: str, values: list
    ) -> None:
        self.type = type
        self.name = name
        self.description = description
        self.null_value = null_value
        self.values = values

    def get_values(self):
        return [self.null_value] + self.values


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

    def get_type(self):
        if self.enum is not None:
            return self.enum.type
        else:
            return self.type


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

            for _ in range(8 - len(row_entries)):
                row_entries.append("")

            id, section, address, size, name, description, type, shown = [
                e.strip() for e in row_entries
            ]

            id = int(id)

            if section != "*":
                section = int(section)

            address = parse_int(address)
            size = parse_int(size)
            description = bytes(description, "utf-8").decode("unicode_escape")
            shown = parse_bool(shown)
            enum = None

            if type == "enum":
                enum_name = row_entries[-1].strip()
                enum = self.get_enum(enum_name)

            self.field_entries.append(
                SettingsFieldEntry(
                    id, section, address, size, name, description, type, shown, enum
                )
            )

    def load_enums_from_data(self, data: list) -> None:
        for line in data:
            if not line.startswith("E"):
                continue

            enum = [e.strip() for e in line.split(";")]

            type, name, description, null_value = enum[1:5]
            values = enum[5:]

            self.enum_entries.append(
                SettingsEnumEntry(type, name, description, null_value, values)
            )

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
