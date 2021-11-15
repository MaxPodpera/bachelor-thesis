import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut


class Messenger:

    rfm95 = None

    def __init__(self):
        self._init_rfm()

    def _init_rfm(self):
        pin_cs = DigitalInOut(board.CE1)
        pin_rst= DigitalInOut(board.D25)
        pin_spi= busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1_000_000
        frequency= 868.0
        self.rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        self.rfm95.tx_power = 23
        self.enable_crc = True
