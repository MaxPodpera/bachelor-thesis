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
        packages: [(int, int, int, int, bytes)] = message.split()
        success: bool = True
        left_over: [Message, None] = None
        try:
            while len(packages) > 0:
                id_to, id_from, header_id, flags, data = packages.pop(0)
                # While messages are being sent continue
                if success:
                    self._rfm95.destination = id_from

                    success = self._rfm95.send_with_ack(data)
                    sleep(.3)
                    continue
                # Otherwise combine prepared messages to packages.
                else:
                    logging.debug("Could not send. wrapping up")
                    package: bytearray = id_to.to_bytes(1, 'big', False) + \
                        id_from.to_bytes(length=1, byteorder='big', signed=False) + \
                        header_id.to_bytes(length=1, byteorder='big', signed=False) + \
                        flags.to_bytes(length=1, byteorder='big', signed=False) + \
                        data
                    m: Message = to_message(package)

                    if left_over is None:
                        print(left_over)
                        left_over = m
                    else:
                        left_over.combine(m)
                    print(m)
                    print(package[:4])
                    print(package[4:])
                    print("LEFT OVER 2" + str(left_over), package)
            print("LEFT OVER" + str(left_over))
            return left_over
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
