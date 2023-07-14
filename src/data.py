import os
import sys
from pathlib import Path
from struct import pack, unpack


def resource_path(relative_path: str) -> Path:
    current_path = Path(".")
    if hasattr(sys, "_MEIPASS"):
        current_path = Path(sys._MEIPASS)
    else:
        current_path = Path(os.path.dirname(__file__))
    return current_path.joinpath(relative_path)


def replace_byte_array(fdata: bytes, position: int, value: bytes):
    fdata = bytearray(fdata)
    for i in range(0, len(value)):
        fdata[position + i] = value[i]
    fdata = bytes(fdata)
    return fdata


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


# def read_str(fdata: bytes, position: int = 0x0) -> str:
#     string = ""
#     offset = 0x0
#     while read_byte_array(fdata, position + offset, 0x1) != b"\x00":
#         string += chr(read_uchar(fdata, position + offset))
#         offset += 1
#     return string


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


def string_to_bytearray(string: str, required_size: int = None):
    try:
        ba = string.encode("shift_jis")
    except Exception as e:
        ba = string.encode("utf-8")

    if required_size:
        ba = ba + b"\x00" * (required_size - len(ba))
    return ba


def read_byte_array(fdata: bytes, position: int, size: int) -> bytes:
    if position + size > len(fdata):
        size = len(fdata) - position
    return fdata[position : position + size]


def sizeof_fmt(num, suffix: str = "B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, "Yi", suffix)


def parse_int(string: str):
    try:
        integer_value = int(string, 16)
    except ValueError:
        try:
            integer_value = int(string)
        except ValueError:
            integer_value = None

    return integer_value


def parse_bool(string: str):
    if string.lower() == "true":
        return True
    else:
        return False


def decode_string(string: str):
    try:
        result = string.decode("utf-8")
    except UnicodeDecodeError as _:
        result = string.decode("shift_jis")
    return result


def int_to_color(value: int):
    alpha = (value >> 24) & 0xFF
    blue = (value >> 16) & 0xFF
    green = (value >> 8) & 0xFF
    red = value & 0xFF

    alpha = (alpha / 255) * 100

    return (red, green, blue, alpha)


def color_to_int(color: tuple):
    try:
        red, green, blue, alpha = color
    except ValueError as _:
        red, green, blue = color
        alpha = 100.0
    alpha = int((alpha / 100) * 255)
    return (alpha << 24) + (int(blue) << 16) + (int(green) << 8) + int(red)
