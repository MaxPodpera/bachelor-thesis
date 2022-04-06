from crccheck.crc import Crc32, CrcXmodem
from src.Utilities import *

length_error_detection: int = int(read_config_file("message.meta.length_error_detection"))


def _calc_checksum(d):
    crcinst = CrcXmodem()
    crcinst.process(d)
    return crcinst.finalbytes()


def remove_and_check(d: bytes) -> (bool, bytes):
    data: bytes = d[:-length_error_detection]
    checksum: bytes = _calc_checksum(data)
    return checksum == d[-length_error_detection:], data


def add_check(d: bytes):
    return bytearray(d) + _calc_checksum(d)


class ErrorDetection:
    pass
