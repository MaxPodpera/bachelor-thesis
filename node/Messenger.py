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
        print("Node id: " + str(self.node_id))
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
        """
        Handling of received messages. If its a message that was sent as one package it is stored.
        Otherwise it is added to the incomplete messages list. If all packets for a message
        are received the complete message is stored.
        :param message: to be handled
        :return: None
        """
        if message._related_packages == 0:  # only a single message
            logging.debug("single message")
            self.storage.store(message)
            return

        if str(message.message_id) not in self.incomplete_messages:  # first message
            logging.debug("First of many")
            self.incomplete_messages[str(message.message_id)] = [message]
            return

        # append message to list
        self.incomplete_messages[str(message.message_id)].append(message)
        logging.debug("One of many")
        # all messages received.
        current_sequence_number: int = 0
        full_message: Message
        if len(self.incomplete_messages[str(message.message_id)]) + 1 == message._related_packages:
            logging.debug("All of many")
            for i in range(message._related_packages):
                for m in self.incomplete_messages[str(message.message_id)]:
                    if m.sequence_number == 0:
                        full_message = m
                        current_sequence_number += 1
                        break
                    elif m.sequence_number == current_sequence_number:
                        full_message.combine(m)
                        current_sequence_number += 1
                        break
            self.storage.store(full_message)
            del self.incomplete_messages[str(message.message_id)]
            return
