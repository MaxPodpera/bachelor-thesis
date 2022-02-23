from __future__ import annotations
import time
import math
from util.Utilities import read_config_file

"""
Message class. Contains definition of the Messages and functionality to convert messages to bytes and the other way around.
"""

address_broadcast: str = read_config_file("message.broadcast_address")


class Message:

    message_id: int = 0
    data: str = None
    recipient: str = address_broadcast     # Broadcast address
    pid: int = 0
    sender: str = "00000000000000000000000000000000"  # todo maybe private
    sender_pid: int = 0
    time: time = None
    sequence_number: int = 0  # Number of this package for the message
    _related_packages: int = 0  # How many other packages for this message

    def __str__(self) -> str:
        """
        For printing only
        :return:
        """
        return "Message{\nto:" + str(self.recipient) + ",\nfrom:" + self.sender + ",\ndata:" + self.data \
               + ",\nsequence_number:" + str(self.sequence_number) + ",\nrelated_packages:" \
               + str(self._related_packages) + "\n}"

    def combine(self, message: Message) -> bool:
        if message.message_id != self.message_id: return False
        if message.recipient != self.recipient: return False
        if message.pid != self.pid: return False
        if message.sender != self.sender: return False
        if message.sender_pid != self.sender_pid: return False
        if message.sequence_number > self._related_packages: return False
        if message.related_packages < self.sequence_number: return False

        print("Combining: " + self.data)
        print("And: " + message.data)
        self.data += message.data
        return True

    @property
    def related_packages(self):
        return self._related_packages

    # TODO is this needed
    @related_packages.setter
    def related_packages(self, value):
        self._related_packages = value