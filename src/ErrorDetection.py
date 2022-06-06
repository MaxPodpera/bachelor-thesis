from crccheck.crc import CrcXmodem
from src.Utilities import *

length_error_detection: int = int(read_config_file("message.meta.length_error_detection"))


def _calc_checksum(d):
    """
    Calculate checksum for messages
    """
    crcinst = CrcXmodem()
    crcinst.process(d)
    return crcinst.finalbytes()


def remove_and_check(d: bytes) -> (bool, bytes):
    """
    Remove the checksum and check if it is correct.
    :return: (true, data) for correct data, (false, data) for incorrect checksum
    """
    data: bytes = d[:-length_error_detection]
    checksum: bytes = _calc_checksum(data)
    return checksum == d[-length_error_detection:], data


def add_check(d: bytes):
    """
    Add check to the data.
    """
    return bytearray(d) + _calc_checksum(d)


class ErrorDetection:
    pass
