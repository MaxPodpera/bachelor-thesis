import board
import busio
import adafruit_rfm9x
import threading
import time
from digitalio import DigitalInOut

from Independent import Independent
from MessageStorage import MessageStorage


class Messenger(Independent):

    rfm95: adafruit_rfm9x.RFM9x = None
    storage: MessageStorage  # Access storage

    node_id = None  # Own id to check how to handle messages
    send_queue: [] = None  # list of next messages to send

    def __init__(self):
        print("init")
        self._init_rfm()
        self.node_id = self._get_node_id()
        self.rfm95.identifier = 255
        self.rfm95.node = 255
        super().__init__()

    def _get_node_id(self):
        import os
        os.system("blkid")
        tmp = " ,"
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
        pin_rst = DigitalInOut(board.D25)
        pin_spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1000000
        frequency = 868.0
        self.rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        print("init_rfm: ", self.rfm95)
        self.rfm95.tx_power = 23
        self.enable_crc = True

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
        print("send: ", self.rfm95)
        while self.active:
            received = self.rfm95.receive()

            # previous loop received a message. Check for more
            if received:
                self.storage.store(received)
                print(received)
                received = None
                continue

            # Noting to send
            if self.send_queue == [] or self.send_queue is None:
                continue

            self.rfm95.send(bytes(self.send_queue[0]))
            self.send_queue = self.send_queue[1:]

    def send(self, data):
        self.send_queue.append(data)

    def _forward(self, package):
        pass
