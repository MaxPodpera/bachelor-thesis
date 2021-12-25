import logging
from node.RFMWrapper import RFMWrapper
from node.Independent import Independent
from node.MessageStorage import MessageStorage
from node.Message import Message
from util.Utilities import *


ms_keep_message_in_storage = 50000


class Messenger(Independent):

    rfm95: RFMWrapper = None  # Access transponder
    storage: MessageStorage = None  # Access storage

    send_queue: [] = []  # list of next messages to send
    known_messages: [] = []
    incomplete_messages: {} = {}
    node_id: str = None

    def __init__(self):
        self.storage = MessageStorage()
        self.rfm95 = RFMWrapper()
        self.node_id = read_uuid_file(read_config_file("uuid_file"))
        super().__init__()

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
        while self.active:
            received: Message = self.rfm95.receive()  # Receive new message
            if received:
                if received.recipient != self.node_id:
                    logging.info("Received message to be forwarded: ")
                    self.rfm95.send(received)
                else:
                    logging.info("Received message for self: ")
                    self.storage.store(received)
                logging.info(received)
                continue  # attempt receiving more messages before sending  PRIORITY ON FORWARDING / RECEIVING

            # Nothing to send
            if self.send_queue == [] or self.send_queue is None:
                logging.info("Nothing received, nothing to send")
                continue

            # something to send
            logging.info("Nothing received, sending")
            self.rfm95.send(self.send_queue[0])
            self.send_queue = self.send_queue[1:]

    def send(self, data: Message) -> None:
        data.sender = self.node_id
        self.send_queue.append(data)

    def handle_received_message(self, message: Message) -> None:
        if message.related_packages == 0: # only a single message
            self.storage.store(message)
            return

        if str(message.message_id) in self.incomplete_messages:  # first message
            self.incomplete_messages[str(message.message_id)] = [message]
            return

        # append message to list
        self.incomplete_messages[str(message.message_id)][message.sequence_number] = message

    def test(self, message):
        self.handle_received_message(message)
        print(self.incomplete_messages)