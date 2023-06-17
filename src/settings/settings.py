from data import parse_int


class SettingsEntry:
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
    ) -> None:
        self.id = id
        self.section = section
        self.address = addresss
        self.size = size
        self.name = name
        self.description = description
        self.type = type
        self.shown = shown


class Settings:
    def __init__(self, data: list = []) -> None:
        self.entries = []
        self.load_entries_from_data(data)

    def load_entries_from_data(self, data: list) -> None:
        for line in data:
            if line.startswith("#") or line.strip() == "":
                continue

            row_entries = line.split(";")

            for _ in range(8 - len(row_entries)):
                row_entries.append("")

            id, section, address, size, name, description, type, shown = [
                e.strip() for e in row_entries
            ]

            id = parse_int(id)
            address = parse_int(address)
            section = parse_int(section)
            size = parse_int(size)
            shown = bool(shown)

            self.entries.append(
                SettingsEntry(
                    id, section, address, size, name, description, type, shown
                )
            )

    def get_entries_in_param(self, param_id: int, section: int = None) -> list:
        if section is not None:
            return [
                entry
                for entry in self.entries
                if (entry.id == param_id and entry.section == section)
            ]
        else:
            return [entry for entry in self.entries if entry.id == param_id]
