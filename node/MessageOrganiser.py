from node.Message import *
from util.Utilities import read_config_file
from typing import Union
import threading
import math

ms_memorize_received_message_id = read_config_file("message.ms_memorize_received_message_id")
broadcast_address = read_config_file("message.broadcast_address")


class MessageOrganiser:

    list_addresses_self: [str] = [broadcast_address]  # Addresses for which messages are stored (if set as recipient)

    queue_received: [(int, str, int)] = []  # Received Messages
    queue_send: [Message] = []  # To be sent
    queue_to_be_completed: {(int, str): [Message]} = {}  # not all packages received yet

    def __init__(self, node_id: str):
        self.list_addresses_self.append(node_id)

    def run(self):
        # Todo empty receive queue when necessary.
        pass

    def push_to_send(self, message: Message):
        """
        Add package to list of packages to be sent. An id will be added if non exists.
        :param message: bytearray as produced by Message.to_bytes
        :return: void
        """
        # TODO add an id.
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
        if self.was_received((message.message_id, message.sender, message.sequence_number)):
            return

        # Not yet received
        self.queue_received.append((message.message_id, message.sender, message.sequence_number))  # add to known message list

        # Message not meant for this node. Add to list to send later
        if not (message.recipient in self.list_addresses_self):
            self.push_to_send(message)
            return

        # Handle message that is meant for this node
        print(message)
        self._handle_message(message)

    def was_received(self, message_distinquisher: (str, str, int)) -> bool:
        """
        Check if message was received before.
        :param message_distinquisher: to check if it was received
        :return: true if it was received false otherwise
        """
        return message_distinquisher in self.queue_received

    def _handle_message(self, message: Message) -> Union[Message, None]:
        """
        Check if message is split in multiple packages. Returns a message if it is complete
        :param message: to be checked
        :return: Message if it is complete, None otherwise
        """
        # Single message
        if message.related_packages == 0:
            print("just one")
            return message

        # First of multiple packages for this message
        if (message.message_id, message.sender) not in self.queue_to_be_completed:
            print("first of many")
            self.queue_to_be_completed[(message.message_id, message.sender)] = [message]
            return None

        # TODO is this thread safe
        self.queue_to_be_completed[(message.message_id, message.sender)].append(message)
        
        # Check if all corresponding packages were received
        if len(self.queue_to_be_completed[(message.message_id, message.sender)]) != message.related_packages + 1:
            print("one of many")
            return None  # Not all received yet

        return self._build_message(self.queue_to_be_completed[(message.message_id, message.sender)])

    def _build_message(self, message_packages: [Message]) -> Message:
        """
        Given a list of related packages (parts of the same message as determined by message id and sender) the messages
         are combined to one message
        :param message_packages: the parts
        :return: the combined message
        """
        if message_packages is None or not message_packages:
            return None

        full_message: Message
        for i in range(0, message_packages[0].related_packages):
            a = [m for m in message_packages if m.sequence_number == i]
            if len(a) != 1:
                logging.error("Transforming message failed")
            if i == 0:
                full_message = a[0]
            else:
                full_message.combine(a[0])
       
        print("full message", full_message)
        # Remove from incomplete list
        del self.queue_to_be_completed[(full_message.message_id, full_message.sender)]
        print("Full fucking message:")
        print("\n\n\n")
        print(full_message)
        return full_message
