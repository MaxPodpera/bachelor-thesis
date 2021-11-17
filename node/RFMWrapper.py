import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut
from Message import Message, from_bytes, to_bytes

# Overwrite a
from micropython import const

adafruit_rfm9x.RFM9x._RH_RF95_REG_0E_FIFO_TX_BASE_ADDR = const(0x0E)
adafruit_rfm9x.RFM9x._RH_RF95_REG_0F_FIFO_RX_BASE_ADDR = const(0x0F)


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
        self.rfm95.destination = 255
        self.rfm95.enable_crc = True
        self.rfm95.identifier = 255
        self.rfm95.node = 255

    def send(self, data: Message):
        """
        Takes a message object to be send. If the message is too large to be sent
        as one, multiple messages will be send.
        :param data: to be sent
        :return: void
        """
        messages = to_bytes(data)
        while messages is not []:
            a = self.rfm95.send(messages[0])
            messages = messages[0:]

    def receive(self) -> Message:
        """
        Receive data from the module. Data will be converted to message object.
        :return: Message object containing the message or None if nothing was received
        """
        # TODO handle split messages
        d = self.rfm95.receive()
        m = from_bytes(d)
        print(m)
        return m

    def _get_node_id(self):
        with open("/proc/cpuinfo", "r") as file:
            for line in file:
                if "Serial" in line:
                    a = line.split(" ")
                    print("ids: ", a)
                    print(a[2])
                    return a
            return None
