from src.Message import *
from src.Utilities import read_config_file
from typing import Union
import time
import threading
import math
import logging
from src.MessageStorage import MessageStorage
from time import sleep

ms_memorize_received_message_id = read_config_file("message.ms_memorize_received_message_id")
broadcast_address = read_config_file("message.broadcast_address")
length_message_id = read_config_file("message.meta.length_message_id")


class MessageOrganiser:
    _active: bool = True

    _message_id_max_value: int = int.from_bytes(bytes.fromhex('ff' * int(length_message_id)), byteorder='big')
    _node_id: str
    _message_id: int = 0
    _storage: MessageStorage = MessageStorage()
    list_addresses_self: [str] = [broadcast_address]  # Addresses for which messages are stored (if set as recipient)

    queue_received: [((int, int, str, int), time)] = []  # Received Messages
    queue_send: [Message] = []  # To be sent
    queue_to_be_completed: {(int, str): [Message]} = {}  # not all packages received yet

    def __init__(self, node_id: str):
        self.list_addresses_self.append(node_id)
        self._node_id = node_id

    def run(self):
        t = threading.Thread(target=self._storage.run)
        t.start()

        while self._active:
            try:
                # Get new Messages
                message: Message = self._storage.get()

                # Add messages to list to be sent
                if message:
                    logging.debug("Got message from storage")
                    self.push_to_send(message)

                # Remove elements from received list if they are expired
                self._clear_expired_from_received()
            except Exception as e:
                logging.error("Error during organiser operation: " + str(e))

        self._storage.stop()
        t.join()

        logging.info("Message organiser shut down!")

    def stop(self):
        self._active = False

    def push_to_send(self, message: Message):
        """
        Add package to list of packages to be sent. An id will be added if non exists.
        :param message: bytearray as produced by Message.to_bytes
        :return: void
        """
        message.sender = self._node_id
        # Set the message id.
        message.message_id = self._message_id
        self._message_id = self._message_id % self._message_id_max_value

        # Add to queue
        self.queue_send.append(message)

    def pop_from_send(self) -> Union[Message, None]:
        """
        Get element from the list of Messages to be sent.
        The element is then removed from they queue
        :return: the package.
        """
        try:
            return self.queue_send.pop(0)
        except IndexError:
            return None

    def push_to_received(self, message: Message):
        """
        Add message to received list. If it is a single message or the last
        of a Message the message is returned.
        :param message: received message
        :return: void
        """
        # Already received
        if self.was_received(message):
            logging.debug("Message already received")
            return
        # Message was sent by this node. Forwarding of neighbour received.
        if message.sender == self._node_id:
            logging.debug("Message forwarding received")
            return

        logging.info("Received unknown Message")
        
        # Not yet received
        self._push_to_received(message)  # add to known message list

        # Message not meant for this node. Add to list to send later
        if not (message.recipient in self.list_addresses_self):
            logging.info("Forwarding message")
            self.queue_send.append(message)
            return

        # Handle message that is meant for this node
        self._handle_message(message)

    def _push_to_received(self, message: Message):
        """
        Add item to received list
        :param message to be added.
        :return:
        """
        message_distinquisher = message.message_id, message.message_sender_header, message.sender, message.sequence_number
        print("Add to received\t", message_distinquisher)
        self.queue_received.append((message_distinquisher, time.time()))
        print(str(self.queue_received))

    def was_received(self, message: Message) -> bool:
        """
        Check if message was received before.
        :param message to be checked
        :return: true if it was received false otherwise
        """
        message_distinquisher = message.message_id, message.message_sender_header, message.sender, message.sequence_number
        print("Check exists\t", message_distinquisher)
        # Search for matching items
        for i in self.queue_received:
            distinquisher, _ = i
            if distinquisher == message_distinquisher:
                return True
        return False

    def _clear_expired_from_received(self):
        """
        Remove items from the received list that expired according to as set time.
        :return:
        """
        for i in range(0, len(self.queue_received)):
            message, rec_time = self.queue_received[i]
            print("hearst", rec_time, time.time() + int(ms_memorize_received_message_id), message)
            if rec_time + int(ms_memorize_received_message_id) > time.time():
                # remove from received list.
                del self.queue_received[i]
                # remove from list of partly received messages
                del self.queue_to_be_completed[(message.message_id, message.sender)]

    def _handle_message(self, message: Message) -> Union[Message, None]:
        """
        Check if message is split in multiple packages. Returns a message if it is complete
        :param message: to be checked
        :return: Message if it is complete, None otherwise
        """
        # Single message
        if message.related_packages == 0:
            logging.debug("Received single message")
            return message

        # First of multiple packages for this message
        if (message.message_id, message.sender) not in self.queue_to_be_completed:
            logging.debug("Received first of many packages")
            self.queue_to_be_completed[(message.message_id, message.sender)] = [message]
            return None

        # TODO is this thread safe
        self.queue_to_be_completed[(message.message_id, message.sender)].append(message)
        
        # Check if all corresponding packages were received
        if len(self.queue_to_be_completed[(message.message_id, message.sender)]) != message.related_packages + 1:
            logging.debug("Received further package of large message")
            return None  # Not all received yet

        logging.debug("Received all packages for message")

        message: Message = self._build_message(self.queue_to_be_completed[(message.message_id, message.sender)])

        # Store message if all parts were received.
        if message is not None:
            self._storage.store(message)

    def _build_message(self, message_packages: [Message]) -> Union[None, Message]:
        """
        Given a list of related packages (parts of the same message as determined by message id and sender) the messages
         are combined to one message
        :param message_packages: the parts
        :return: the combined message
        """
        logging.debug("Combining messages")
        if message_packages is None or not message_packages:
            return None

        full_message: Message = Message()
        for i in range(0, message_packages[0].related_packages + 1):
            # Get current element.
            a = [m for m in message_packages if m.sequence_number == i]
            if len(a) != 1:
                logging.error("Transforming message failed")
                return None
            if i == 0:
                full_message = a[0]
            else:
                full_message.combine(a[0])

        # Remove from incomplete list
        del self.queue_to_be_completed[(full_message.message_id, full_message.sender)]
        # Return full message
        return full_message