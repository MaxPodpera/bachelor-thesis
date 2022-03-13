import board
import busio
import adafruit_rfm9x
import time
from digitalio import DigitalInOut
from node.Message import *
from time import sleep
from micropython import const
"""
Class to wrap the rfm95 module access in.
"""


class RFMWrapper:

    _rfm95: adafruit_rfm9x.RFM9x = None
    _sequence_id: int = 0
    
    def __init__(self):
        pin_cs = DigitalInOut(board.CE1)
        pin_rst = DigitalInOut(board.D25)
        pin_spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1000000
        frequency = 868.0
        self._rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        self._rfm95.tx_power = 23
        # self._rfm95.destination = 255
        self._rfm95.enable_crc = True
        # self._rfm95.identifier = 255
        # self._rfm95.node = 255

    def send(self, data: Message) -> bool:
        """
        Takes a message object to be send. If the message is too large to be sent
        as one, multiple packages will be send.
        :param data: to be sent
        :return: void
        """
        # Message to package
        packages: [(int, int, int, int, bytes)] = data.split()
        success: bool = True

        while len(packages) > 0 and success:
            id_from, id_to, message_id, flags, message = packages.pop(0)
            success &= self._rfm95.send(message,
                                        destination=id_to,
                                        node=id_from,
                                        identifier=message_id + len(packages),
                                        flags=flags)
            
            print("\n\n\n", str(message), success, "\n\n\n")
        return success

    def receive(self) -> Union[Message, None]:
        """
        Receive data from the module. Data will be converted to message object.
        :return: Message object containing the message or None if nothing was received
        """
        print("Checking for messages")
        d = self._rfm95.receive(with_header=True)
        if d is None:
            return None
        print("\n\nRECEIVED\n", d, "\n\n")
        return to_message(d)


# TODO:
# Wird wirklich das empfangene geprintet
# Wird wirklich gesendet? ID think so
