from RFMWrapper import RFMWrapper
from Independent import Independent
from MessageStorage import MessageStorage


class Messenger(Independent):

    rfm95: RFMWrapper = None  # Access transponder
    storage: MessageStorage = None  # Access storage

    node_id = None  # Own id to check how to handle messages
    send_queue: [] = None  # list of next messages to send

    def __init__(self):
        self.storage = MessageStorage()
        self.rfm95 = RFMWrapper()
        super().__init__()

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
        while self.active:
            received = self.rfm95.receive()  # Receive new message
            print(received)
            if received:
                if received.recipient == self.rfm95.node_id:
                    self.rfm95.send(received)
                else:
                    self.storage.store(received)
                continue  # attempt receiving more messages before sending

            # Nothing to send
            if self.send_queue == [] or self.send_queue is None:
                continue

            # something to send
            self.rfm95.send(self.send_queue[0])
            self.send_queue = self.send_queue[1:]

    def send(self, data):
        self.send_queue.append(data)

    def _forward(self, package):
        pass
