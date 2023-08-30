import os
import sys
from pathlib import Path
from struct import pack, unpack


def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        current_path = Path(sys._MEIPASS)
    else:
        current_path = Path(os.path.dirname(__file__))
    return current_path.joinpath(relative_path)


def replace_byte_array(fdata: bytes, position: int, value: bytes) -> bytes:
    fdata = bytearray(fdata)
    for i in range(0, len(value)):
        fdata[position + i] = value[i]
    fdata = bytes(fdata)
    return fdata


def read_byte_array(fdata: bytes, position: int, size: int) -> bytes:
    if position + size > len(fdata):
        size = len(fdata) - position
    return fdata[position : position + size]


def read_uint(fdata: bytes, position: int = 0x0) -> int:
    return unpack("I", read_byte_array(fdata, position, 4))[0]


def read_ushort(fdata: bytes, position: int = 0x0) -> int:
    return unpack("H", read_byte_array(fdata, position, 2))[0]


def read_uchar(fdata: bytes, position: int = 0x0) -> int:
    return unpack("B", read_byte_array(fdata, position, 1))[0]


def read_int(fdata: bytes, position: int = 0x0) -> int:
    return unpack("i", read_byte_array(fdata, position, 4))[0]


def read_short(fdata: bytes, position: int = 0x0) -> int:
    return unpack("h", read_byte_array(fdata, position, 2))[0]


def read_char(fdata: bytes, position: int = 0x0) -> int:
    return unpack("b", read_byte_array(fdata, position, 1))[0]


def read_bool(fdata: bytes, position: int = 0x0) -> int:
    return unpack("?", read_byte_array(fdata, position, 1))[0]


def read_float(fdata: bytes, position: int = 0x0) -> int:
    return unpack("f", read_byte_array(fdata, position, 4))[0]


def read_str(fdata: bytes, position: int = 0x0) -> str:
    string_bytes = bytearray()
    offset = 0x0
    while (last_byte := read_uchar(fdata, position + offset)) != 0x00 and offset < len(
        fdata
    ) - 1:
        string_bytes.append(last_byte)
        offset += 1
    try:
        string = unpack(f"{len(string_bytes)}s", string_bytes)[0].decode("utf-8")
    except UnicodeDecodeError as _:
        string = unpack(f"{len(string_bytes)}s", string_bytes)[0].decode("shift_jis")

    return string


def read_str_short(fdata: bytes, position: int = 0x0) -> str:
    string_bytes = bytearray()
    offset = 0x0
    while (
        last_bytes := read_ushort(fdata, position + offset)
    ) != 0x00 and offset < len(fdata) - 1:
        string_bytes += pack("H", last_bytes)
        offset += 2
    try:
        string = unpack(f"{len(string_bytes)}s", string_bytes)[0].decode("utf-16")
    except UnicodeDecodeError as _:
        string = unpack(f"{len(string_bytes)}s", string_bytes)[0].decode("shift_jis")

    return string


def string_to_bytearray(string: str, required_size: int = None) -> bytes:
    try:
        ba = string.encode("shift_jis")
    except UnicodeDecodeError as _:
        ba = string.encode("utf-8")

    if required_size:
        ba = ba + b"\x00" * (required_size - len(ba))
    return ba


def bytearray_to_string(byte_array: bytearray) -> str:
    last_non_zero_index = len(byte_array) - 1
    while last_non_zero_index >= 0 and byte_array[last_non_zero_index] == 0:
        last_non_zero_index -= 1

    trimmed_byte_array = byte_array[: last_non_zero_index + 1]

    try:
        decoded_str = trimmed_byte_array.decode("utf-8")
    except UnicodeDecodeError:
        try:
            decoded_str = trimmed_byte_array.decode("shift_jis")
        except UnicodeDecodeError:
            decoded_str = None

    return decoded_str


def sizeof_fmt_new(num: int, suffix: str = "B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def parse_int(string: str) -> int | None:
    try:
        integer_value = int(string, 16)
    except ValueError:
        try:
            integer_value = int(string)
        except ValueError:
            integer_value = None

    return integer_value


def parse_bool(string: str) -> bool:
    if string.lower() == "true":
        return True
    else:
        return False


def decode_string(string: bytes) -> str:
    try:
        result = string.decode("utf-8")
    except UnicodeDecodeError as _:
        result = string.decode("shift_jis")
    return result


def int_to_color(value: int) -> tuple:
    alpha = (value >> 24) & 0xFF
    blue = (value >> 16) & 0xFF
    green = (value >> 8) & 0xFF
    red = value & 0xFF
    return red, green, blue, alpha


def color_to_int(color: tuple) -> int:
    try:
        red, green, blue, alpha = color
    except ValueError as _:
        red, green, blue = color
        alpha = 100.0
    return (alpha << 24) + (int(blue) << 16) + (int(green) << 8) + int(red)


def validate_byte_string(input_string: str) -> bool:
    byte_values = input_string.split()

    if any((len(byte) % 2 != 0 for byte in byte_values)):
        return False

    try:
        for byte in byte_values:
            int(byte, 16)
    except ValueError:
        return False

    return True


def string_to_bytes(string: str) -> bytearray:
    byte_values = string.split()
    byte_array = bytearray()

    for byte in byte_values:
        byte_array.append(int(byte, 16))

    return byte_array


def bytes_to_string(b: bytes) -> str:
    return " ".join(["{:02X}".format(byte) for byte in b])
