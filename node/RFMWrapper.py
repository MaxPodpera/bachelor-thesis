import board
import busio
import adafruit_rfm9x
import time
from digitalio import DigitalInOut
from node.Message import *
# Overwrite a
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
        self._rfm95.destination = 255
        self._rfm95.enable_crc = False
        self._rfm95.identifier = 255
        self._rfm95.node = 255

    def send(self, data: Message) -> bool:
        """
        Takes a message object to be send. If the message is too large to be sent
        as one, multiple packages will be send.
        :param data: to be sent
        :return: void
        """
        # Message to package
        packages: [((int, int, int, int), bytes)] = data.split()
        success: bool = True
        while len(packages) > 0 and success:
            headers, data = packages.pop(0)
            to_id, from_id, message_id, flags = headers
            print("Here", headers, data)
            success &= self._rfm95.send(data,
                                        destination=to_id,
                                        node=from_id,
                                        identifier=message_id,
                                        flags=flags)
        return success

    def receive(self) -> Union[Message, None]:
        """
        Receive data from the module. Data will be converted to message object.
        :return: Message object containing the message or None if nothing was received
        """
        d = self._rfm95.receive(with_header=True)
        if d:
            headers = d[:4]
            data = d[4:]
            return to_message(headers, data)
        return None

# TODO:
#Wir wirklich das empfangene geprintet
#Wir wirklich gesendet? ID think so