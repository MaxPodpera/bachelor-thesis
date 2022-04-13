from src.Message import *
from src.Utilities import read_config_file
from typing import Union
import time
import threading
import logging
from src.MessageStorage import MessageStorage

ms_memorize_received_message_id: int = int(read_config_file("message.ms_memorize_received_message_id"))
broadcast_address = read_config_file("message.broadcast_address")
length_message_id = read_config_file("message.meta.length_message_id")


def _create_distinquisher(message: Message) -> (int, int, str):
    """
    Create message distinguisher used for identifying packages.
    """
    return message.sender, message.message_id, message.sequence_number


class MessageOrganiser:
    _active: bool = True

    _message_id_max_value: int = int.from_bytes(bytes.fromhex('ff' * int(length_message_id)), byteorder='big')
    _node_id: str
    _message_id: int = 0
    _storage: MessageStorage = MessageStorage()
    list_addresses_self: [str] = [broadcast_address]  # Addresses for which messages are stored (if set as recipient)

    queue_received: [((int, int, str), time)] = []  # Received Messages
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
                self._clear_expired_from_queue()

            except Exception as e:
                logging.error("Error during organiser operation: " + str(e))

        self._storage.stop()
        t.join()

        logging.info("Message organiser shut down!")

    def stop(self):
        self._active = False

    def push_to_send(self, message: Message):
        """
        Add package to list of packages to be sent. An id and sender will be added if non exists.
        :param message: bytearray as produced by Message.to_bytes
        :return: void
        """
        if message.sender is None:
            logging.debug("Adding sender id")
            message.sender = self._node_id
        # Set the message id
        if message.message_id is None:
            logging.debug("Adding message id")
            message.message_id = self._message_id
            self._message_id = (self._message_id + 1) % self._message_id_max_value

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

    def push_to_received(self, package: Message):
        """
        Add package to received list. If it is a single message or the last
        of a Message the message is returned.
        :param package: received message
        :return: void
        """
        # Already received
        if self.was_received(package):
            logging.debug("Package already received")
            return

        # Message was sent by this node. Forwarding of neighbour received.
        if package.sender == self._node_id:
            logging.debug("Package forwarding received")
            return

        logging.info("Received unknown Package")
        
        # Not yet received
        self._push_to_received(package)  # add to known message list

        # Message not meant for this node. Add to list to send later
        if not (package.recipient in self.list_addresses_self):
            logging.info("Forwarding message")
            self.push_to_send(package)
            return

        # Handle message that is meant for this node
        m: Message = self._handle_message(package)
        if m is None:
            return
        self._storage.store(m)

    def _push_to_received(self, message: Message):
        """
        Add item to received list
        :param message to be added.
        :return:
        """
        message_distinquisher = _create_distinquisher(message)
        self.queue_received.append((message_distinquisher, time.time()))

    def was_received(self, message: Message) -> bool:
        """
        Check if message was received before.
        :param message to be checked
        :return: true if it was received false otherwise
        """
        message_distinquisher = _create_distinquisher(message)

        # Search for matching items
        print("\t\t\tqueue", self.queue_received)
        for i in self.queue_received:
            distinquisher, _ = i
            if distinquisher == message_distinquisher:
                return True
        return False

    def _clear_expired_from_queue(self):
        """
        Remove items from the received list that expired according to as set time.
        :return:
        """
        try:
            i: int = 0
            final: int = len(self.queue_received)
            while i < final:
                message, rec_time = self.queue_received.pop()
                print("\t\t\tcheck", rec_time, time.time())
                print("\t\t\tval", rec_time + ms_memorize_received_message_id)
                print("\t\t\tres", rec_time + ms_memorize_received_message_id <= time.time(), ms_memorize_received_message_id)
                if rec_time + ms_memorize_received_message_id > time.time():
                    # Still valid to keep information
                    self.queue_received.append((message, rec_time))
                else:
                    print("\t\t\tremoving", rec_time)
                    if (message[0], message[2]) in self.queue_to_be_completed:
                        del self.queue_to_be_completed[(message[0], message[2])]
                i += 1  # loop progress
            if final != len(self.queue_received):
                print("\t\t\tchanges", self.queue_received)
        except Exception as e:
            logging.error("Could not clear expired messages: " + str(e))

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

        self.queue_to_be_completed[(message.message_id, message.sender)].append(message)

        # Check if all corresponding packages were received
        if len(self.queue_to_be_completed[(message.message_id, message.sender)]) != message.related_packages + 1:
            logging.debug("Received further package of large message")
            return None  # Not all received yet

        logging.debug("Received all packages for message")

        message: Message = self._build_message(self.queue_to_be_completed[(message.message_id, message.sender)])
        return message

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
