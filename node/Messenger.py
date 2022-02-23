import logging
from node.RFMWrapper import RFMWrapper
from node.Independent import Independent
from node.MessageStorage import MessageStorage
from node.Message import Message
from node.MessageOrganiser import MessageOrganiser
from util.Utilities import *


class Messenger(Independent):

    rfm95: RFMWrapper = None  # Access transponder
    storage: MessageStorage = None  # Access storage
    organiser: MessageOrganiser = MessageOrganiser()
    node_id: str = None

    def __init__(self):
        self.storage = MessageStorage()
        self.rfm95 = RFMWrapper()
        self.node_id = read_uuid_file(read_config_file("uuid_file"))
        print("Node id: " + str(self.node_id))
        super().__init__()

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
        while self.active:
            received: Message = self.rfm95.receive()  # Receive new message
            if received:                              # Check if something was received
                self.organiser.push_to_received(received)  # Add to relevant queues and lists
                continue  # attempt receiving more messages before sending  PRIORITY ON FORWARDING / RECEIVING

            # Check send queue
            package: Message = self.organiser.pop_from_send()
            # Nothing to send
            if package is None:
                continue

            # package to be sent
            if self.rfm95.send(package):
                print(package)
                logging.info("Sent package")
            else:
                self.organiser.push_to_send(package)

    def send(self, data: Message) -> None:
        if data.recipient == self.node_id:
            return
        data.sender = self.node_id
        print("Add to queue")
        self.organiser.push_to_send(data)
