import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut
from Message import Message, from_bytes

class RFMWrapper:

    rfm95: adafruit_rfm9x.RFM9x = None
    node_id: int = 255

    def __init__(self):
        pin_cs = DigitalInOut(board.CE1)
        pin_rst = DigitalInOut(board.D25)
        pin_spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1000000
        frequency = 868.0
        self.rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        self.rfm95.tx_power = 23
        self.rfm95.enable_crc = True
        self.rfm95.identifier = 255
        self.rfm95.node = 255

    def send(self, data):
        a = self.rfm95.send(data)
        print("send: ", a)

    def receive(self) -> Message:
        d = self.rfm95.receive()
        return from_bytes(d)

    def _get_node_id(self):
            # TODO get id
            import os
            os.system("blkid")
            tmp = " ,"
            print(tmp)
            tmp_array = tmp.split()
            print(tmp_array)
            return ""
