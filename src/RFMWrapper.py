import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut
from src.Message import *
from time import sleep
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
        self._rfm95.node = 255  # so all packages will be received
        logging.info("Setup of module complete")

    def send(self, message: Message) -> Union[None, Message]:
        """
        Takes a message object to be send. If the message is too large to be sent
        as one, multiple packages will be send.
        :param message: to be sent
        :return: void
        """
        # Message to package
        logging.info("Sending message")

        try:
            while True:
                package: Union[Message, None] = message.next_package()
                # Nothing to send anymore or error that will not be fixed
                if package is None:
                    return None

                # Unpack values
                id_to, id_from, header_id, flags, data = package
                # While messages are being sent continue
                self._rfm95.destination = id_from

                if not self._rfm95.send_with_ack(data):
                    message.internal_reattach_package(package)
                    break
                sleep(.3)

            return message
        except Exception as e:
            logging.error("Exception while sending data: " + str(e))
            raise MalformedContentException(e)

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

        logging.critical(d[:4])
        message: Message = to_message(d)
        if message is None:
            return None

        logging.info("Received package")
        return message
