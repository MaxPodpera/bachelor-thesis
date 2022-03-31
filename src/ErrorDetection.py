import os
import sys
from crccheck.crc import Crc32, CrcXmodem
from crccheck.checksum import Checksum32
sys.path.append(os.getcwd())
from src.Utilities import *

length_error_detection: int = int(read_config_file("message.meta.length_error_detection"))


def _calc_checksum(d):
    crcinst = CrcXmodem()
    crcinst.process(d)
    return crcinst.finalbytes()


def remove_and_check(d: bytes) -> (bool, bytes):
    data: bytes = d[:-2]
    checksum: bytes = _calc_checksum(data)
    return checksum == d[-2:], data


def add_check(d: bytes):
    return bytearray(d) + _calc_checksum(d)


class ErrorDetection:
    pass
