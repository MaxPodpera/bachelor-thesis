import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut


class Messenger:

    rfm95 = None
    node_id = None

    def __init__(self):
        self._init_rfm()
        self.node_id = self._get_node_id()
        print(self.node_id)

    def _get_node_id(self):
        import os
        tmp = os.system("blkid")
        print(tmp)
        tmp_array = tmp.split()
        print(tmp_array)
        return ""

    def _init_rfm(self):
        """
        Iitialize the rfm device for communication
        :return: void
        """
        pin_cs = DigitalInOut(board.CE1)
        pin_rst= DigitalInOut(board.D25)
        pin_spi= busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1_000_000
        frequency= 868.0
        self.rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        self.rfm95.tx_power = 23
        self.enable_crc = True

    def start(self):
        pass

    def send(self, data):
        pass

    def _forward(self, package):
        pass

if __name__ == '__main__':
    m = Messenger()