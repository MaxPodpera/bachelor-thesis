import board
import busio
import adafruit_rfm9x
import logging
import time
from digitalio import DigitalInOut
from src.Message import *
from time import sleep
from micropython import const
from src.Exceptions import MalformedContentException

"""
Class to wrap the rfm95 module access.
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
        self._rfm95.receive_timeout = 2
        # self._rfm95.destination = 255
        self._rfm95.enable_crc = True
        # self._rfm95.identifier = 255
        # self._rfm95.node = 255

    def send(self, message: Message) -> bool:
        """
        Takes a message object to be send. If the message is too large to be sent
        as one, multiple packages will be send.
        :param message: to be sent
        :return: void
        """
        # Message to package
        logging.info("Sending message")
        packages: [(int, int, int, int, bytes)] = message.split()
        success: bool = True
        try:
            # Send the single packages
            while len(packages) > 0 and success:
                id_from, id_to, identifier, flags, data = packages.pop(0)
                if identifier is None:
                    identifier = self._sequence_id
                    self._sequence_id = (self._sequence_id + 1) % 255
                success &= self._rfm95.send(data,
                                            destination=id_to,
                                            node=id_from,
                                            identifier=identifier,
                                            flags=flags,
                                            keep_listening=True)
                sleep(2)
                print("Sendinge\t", message, id_to, id_from, identifier, flags)
            logging.info("Transmission end")
        except Exception as e:
            logging.error("Exception while sending data: " + str(e))
            raise MalformedContentException(e)
        return success

    def receive(self) -> Union[Message, None]:
        """
        Receive data from the module. Data will be converted to message object.
        :return: Message object containing the message or None if nothing was received
        """
        d = self._rfm95.receive(
            with_header=True,
            keep_listening=True
        )

        if d is None:
            return None
        message: Message = to_message(d)
        print("received \t", message)
        logging.info("Received package")
        return message