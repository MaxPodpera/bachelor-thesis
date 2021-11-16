import threading

import board
import busio
import adafruit_rfm9x
import time
from digitalio import DigitalInOut

#from node.Independent import Independent
#from node.MessageStorage import MessageStorage


class Messenger(Independent):

    rfm95 = None  # rfm95
    storage = MessageStorage()  # Access storage

    node_id = None  # Own id to check how to handle messages
    send_queue = None  # list of next messages to send

    def __init__(self):
        super().__init__()

        self._init_rfm()
        self.node_id = self._get_node_id()
        self.rfm95.identifier = 255
        self.rfm95.node = 255

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
        pin_rst= DigitalInOut(board.D25)
        pin_spi= busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        baudrate = 1_000_000
        frequency= 868.0
        self.rfm95 = adafruit_rfm9x.RFM9x(pin_spi, pin_cs, pin_rst, frequency, baudrate=baudrate)
        self.rfm95.tx_power = 23
        self.enable_crc = True

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
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


if __name__ == '__main__':
    m = Messenger()
    time.sleep(2)
    m.start()
    m.send({"data": "hello there", "recipient": {"pid": "asdsd", "at": "45:32:21:ae:bc"}})
