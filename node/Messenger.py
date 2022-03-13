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
    organiser: MessageOrganiser = None
    node_id: str = None

    def __init__(self):
        self.storage = MessageStorage()
        self.rfm95 = RFMWrapper()
        self.node_id = read_uuid_file(read_config_file("uuid_file"))
        self.organiser = MessageOrganiser(self.node_id)
        super().__init__()

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
        logging.info("Started node with id: " + str(self.node_id))
        self.organiser.start()
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
                logging.info("Sent package")
            else:
                logging.error("Could not send package")
                self.organiser.push_to_send(package)
        
        logging.info("Shut down Messenger")

    def send(self, data: Message) -> None:
        """
        Add message to send queue, if it not destined for this node.
        The sender of the message will be set to this node.
        :param data: message to be sent.
        :return: void.
        """
        if data.recipient == self.node_id:
            return
        logging.info("Adding message to send queue")
        data.sender = self.node_id
        self.organiser.push_to_send(data)
