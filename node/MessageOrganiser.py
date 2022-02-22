from node.Message import *
from util.Utilities import read_config_file
from typing import Union
import threading

ms_memorize_received_message_id = read_config_file("message.ms_memorize_received_message_id")

_lock = threading.Lock()
_message_id: int = 0  # id for new messages.
_message_id_rollover = int(math.pow(10, int(read_config_file("message.meta.length_message_id"))))


class MessageOrganiser:

    list_addresses_self: [str] = []  # Addresses for which messages are stored (if set as recipient)

    queue_received: [str] = []  # Received Messages
    queue_send: [Message] = []  # To be sent
    queue_to_be_completed: {str: [Message]} = {}  # not all packages received yet

    def run(self):
        # Todo empty receive queue when necessary.
        pass

    def push_to_send(self, message: Message):
        """
        Add package to list of packages to be sent. An id well be added if non exists
        :param message: bytearray as produced by Message.to_bytes
        :return: void
        """
        # Add id to the message if there is none
        global _message_id
        if message.message_id == -1:
            with _lock:
                package.message_id = _message_id
                _message_id = (_message_id + 1) % message_id_rollover
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

    async def push_to_received(self, message: Message):
        """
        Add message to received list. If it is a single message or the last
        of a Message the message is returned.
        :param message: received message
        :return: void
        """
        # Already received
        if self.was_received(message.message_id):
            return

        # Not yet received
        self.queue_received.append(message.message_id)  # add to known message list

        # Message not meant for this node. Add to list to send later
        if not (message.recipient in self.list_addresses_self):
            self.push_to_send(message)
            return

        # Handle message that is meant for this node
        await self._handle_message(message)

    def was_received(self, message_id: str) -> bool:
        """
        Check if message was received before.
        :param message_id: to check if it was received
        :return: true if it was received false otherwise
        """
        return message_id in self.queue_received

    def _handle_message(self, message: Message) -> Union[Message, None]:
        """
        Check if message is split in multiple packages. Returns a message if it is complete
        :param message: to be checked
        :return: Message if it is complete, None otherwise
        """
        # Single message
        if message.related_packages == 0:
            return message

        # First of multiple packages for this message
        if str(message.message_id) not in self.queue_to_be_completed:
            self.queue_to_be_completed[str(message.message_id)] = [message]
            return None

        # TODO is this thread safe
        self.queue_to_be_completed[str(message.message_id)].append(message)

        # Check if all corresponding packages were received
        if len(self.queue_to_be_completed[str(message.message_id)]) != message.related_packages:
            return None  # Not all received yet

        # All received build full message
        full_message: Message = None
        current_sequence_number: int = 0
        for i in range(message.related_packages):
            for m in self.queue_to_be_completed[str(message.message_id)]:
                if m.sequence_number == 0:
                    full_message = m
                    current_sequence_number += 1
                    break
                elif m.sequence_number == current_sequence_number:
                    full_message.combine(m)
                    current_sequence_number += 1
                    break
        # Remove from incomplete list
        del self.queue_to_be_completed[str(message.message_id)]
        print("Full fucking message:")
        print(full_message)
        return full_message
