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
        self._rfm95.reset()
        self._rfm95.ack_delay = .1
        ###########
        # see documentation for meaning
        # self._rfm95.ack_delay = .1
        # self._rfm95.ack_retries = 5
        # Wait time before resending
        # self._rfm95.ack_wait = .3
        self._rfm95.node = 255  # so all packages will be received
        logging.info("Setup of module complete")
        print(self._rfm95.signal_bandwidth)
        print(self._rfm95.spreading_factor)

        # identifier will be overwritten by send_with_ack
        # self._rfm95.identifier =
        # self._rfm95.tx_power = 23
        # self._rfm95.receive_timeout = 2

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
        success: bool
        try:
            success = self._send_check_every_package(packages)
        except Exception as e:
            logging.error("Exception while sending data: " + str(e))
            raise MalformedContentException(e)
        return success

    def _send_check_every_package(self, packages: [bytes]) -> bool:
        success: bool = True
        while len(packages) > 0 and success:
            # Get infos
            _, id_to, _, _, data = packages.pop(0)
            # Set this to generate more unique messages.
            self._rfm95.destination = id_to
            # sending
            print("\n")
            print(data)
            print("\n")
            success &= self._rfm95.send_with_ack(data)
            sleep(.3)
            logging.debug("Package sent: " + str(success))
        return success

    def _send_check_with_retries(self, packages: [bytes], retries: int):
        success: bool = True
        while len(packages) > 0 and success:
            _, id_to, _, _, data = packages.pop(0)
            self._rfm95.destination = id_to
            print("\n")
            print(data)
            print("\n")
            retries_remaining: int = retries
            package_success: bool = False
            while not package_success and retries_remaining > 0:
                package_success = self._rfm95.send_with_ack(data)
                logging.info("Send failed, retrying")
                sleep(.3)
            success &= package_success
        return success

    def _send_check_once(self, packages: [bytes]) -> bool:
        while len(packages) > 1:
            _, id_to, _, _, data = packages.pop(0)
            self._rfm95.destination = id_to
            print("\n")
            print(data)
            print("\n")
            self._rfm95.send_with_ack(data)
            sleep(.3)
            logging.debug("Package might have been sent")
        return self._send_check_every_package(packages)

    def receive(self) -> Union[Message, None]:
        """
        Receive data from the module. Data will be converted to message object.
        :return: Message object containing the message or None if nothing was received
        """
        d = self._rfm95.receive(
            with_header=True,
            keep_listening=True,
            with_ack=True
        )

        if d is None:
            return None
        print("\t", self._rfm95.last_rssi)
        print("\t", self._rfm95.last_snr)
        logging.critical(d[:4])
        message: Message = to_message(d)
        if message is None:
            return None

        logging.info("Received package")
        return message
