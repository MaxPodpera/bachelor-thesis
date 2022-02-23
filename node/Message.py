from __future__ import annotations
import time
import math
from util.Utilities import read_config_file
from node.Packet import *
"""
Message class. Contains definition of the Messages and functionality to convert messages to bytes and the other way around.
"""


def to_package(message: Message) -> [Package]:
    """
    Convert message to bytes according to message specification. If Data is to long for transmission in one package
    multiple will be generated. If they exceed the max number of packages within a sequence, packages with the next
    message id will be generated.
    :param message: to be converted
    :return: array containing each message that has to be sent.
    """
    return Packet.from_message(message)


class Message:

    message_id: int = -1
    data: str = None
    recipient: str = address_broadcast     # Broadcast address
    pid: int = -1
    sender: str = "00000000000000000000000000000000"  # todo maybe private
    sender_pid: int = -1
    time: time = None
    sequence_number: int = 0  # Number of this package for the message
    _related_packages: int = -1  # How many other packages for this message

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

    def to_packets(self):
        return Packet.from_message(self)
