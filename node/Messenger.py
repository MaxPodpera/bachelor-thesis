import logging
from RFMWrapper import RFMWrapper
from Independent import Independent
from MessageStorage import MessageStorage
from Message import Message


class Messenger(Independent):

    rfm95: RFMWrapper = None  # Access transponder
    storage: MessageStorage = None  # Access storage

    send_queue: [] = []  # list of next messages to send

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
            received: Message = self.rfm95.receive()  # Receive new message
            if received:
                if received.recipient != self.rfm95.node_id:
                    logging.info("Received message to be forwarded: ")
                    self.rfm95.send(received)
                else:
                    # TODO handle receiving multiple messages because of split
                    logging.info("Received message for self: ")
                    self.storage.store(received)
                logging.info(received)
                continue  # attempt receiving more messages before sending

            # Nothing to send
            if self.send_queue == [] or self.send_queue is None:
                logging.info("Nothing received, nothing to send")
                continue
            logging.info("Nothing received, sending")
            # something to send
            self.rfm95.send(self.send_queue[0])
            self.send_queue = self.send_queue[1:]

    def send(self, data: Message):
        data.sender = self.rfm95.node_id
        self.send_queue.append(data)