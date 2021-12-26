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

    def __init__(self):
        pin_cs = DigitalInOut(board.CE1)
        pin_rst = DigitalInOut(board.D25)
        pin_spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1000000
        frequency = 868.0
        self._rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        self._rfm95.tx_power = 23
        self._rfm95.destination = 255
        self._rfm95.enable_crc = True
        self._rfm95.identifier = 255
        self._rfm95.node = 255

    def send(self, data: Message) -> bool:
        """
        Takes a message object to be send. If the message is too large to be sent
        as one, multiple packages will be send.
        :param data: to be sent
        :return: void
        """
        packages: [bytearray] = to_bytes(data)
        success: bool = True
        print("Message split to be: " + str(packages))
        data.related_packages = len(packages)
        while len(packages) > 0 and success:
            print("SENDING")
            print(packages[0])
            success &= self._rfm95.send(packages[0], keep_listening=True)
            packages = packages[1:]
            time.sleep(1)
        return success

    def receive(self) -> Message:
        """
        Receive data from the module. Data will be converted to message object.
        :return: Message object containing the message or None if nothing was received
        """
        d = self._rfm95.receive()
        if d:
            print("RECEIVED")
            print(d)
        m = from_bytes(d)
        return m
