from __future__ import annotations
import time
from typing import Union

import math
from src.Utilities import read_config_file
import logging
from src.ErrorDetection import add_check, remove_and_check
"""
Message class. Contains definition of the Messages and functionality to convert messages to bytes and the other way around.
"""
length_node_id: int = int(read_config_file("message.meta.length_id"))
length_pid: int = int(read_config_file("message.meta.length_pid"))
length_frame: int = int(read_config_file("message.meta.length_frame"))
length_message_id: int = int(read_config_file("message.meta.length_message_id"))
length_sequence_number: int = int(read_config_file("message.meta.length_sequence_number"))  # length is expected to
# be of even length
length_error_detection: int = int(read_config_file("message.meta.length_error_detection"))
# even length
length_meta: int = (length_node_id * 2) + (length_pid * 2) + length_sequence_number + length_message_id + \
                   length_error_detection
length_max_data: int = length_frame - length_meta


address_broadcast: str = read_config_file("message.broadcast_address")


def to_message(package: bytes) -> Union[Message, None]:
    """
    Convert package to message object.
    If package is invalid (crc check) None is returned.
    """
    if not package or package is None:
        logging.info("empty package. not transforming")
        print("return none")
        return None

    try:
        next_part_index: int = length_node_id
        m: Message = Message()

        # Strip headers
        m._header_to, m._message_sender_header, m._header_id, _ = package[:4]
        bytes_to_convert = package[4:]

        # Check data before converting
        valid, bytes_to_convert = remove_and_check(bytes_to_convert)
        if not valid:
            logging.info("Received invalid package, discarding")
            logging.debug(bytes_to_convert)
            return None

        # To
        m.recipient = bytes_to_convert[:next_part_index].hex()
        m.pid = int.from_bytes(bytes_to_convert[next_part_index: next_part_index + length_pid], byteorder='big',
                               signed=False)
        next_part_index += length_pid

        # From
        m._sender = bytes_to_convert[next_part_index: next_part_index + length_node_id].hex()
        next_part_index += length_node_id
        m.sender_pid = int.from_bytes(bytes_to_convert[next_part_index: next_part_index + length_pid],
                                      byteorder='big', signed=False)
        next_part_index += length_pid

        # Message id
        m.message_id = int.from_bytes(bytes_to_convert[next_part_index: next_part_index + length_message_id]
                                      , byteorder='big', signed=False)
        next_part_index += length_message_id

        # Sequence Number
        m._related_packages = int.from_bytes(
            bytes_to_convert[next_part_index: next_part_index + math.floor(length_sequence_number / 2)],
            byteorder='big', signed=False)
        next_part_index += math.floor(length_sequence_number / 2)

        m.sequence_number = int.from_bytes(
            bytes_to_convert[next_part_index: next_part_index + math.floor(length_sequence_number / 2)],
            byteorder='big', signed=False)
        next_part_index += math.floor(length_sequence_number / 2)

        # Data
        m.data = bytes_to_convert[next_part_index:].decode("utf-8")

        # Time
        m.time = time.time()

        logging.debug("Created message from bytes")
        return m
    except Exception as e:
        print("other exception")
        logging.error("Error while creating message: " + str(e))
        return None


"""
Alias for package type
"""
packageType = (int, int, int, int, bytes)


class Message:
    """
    Class representing messages for the network
    """
    @property
    def recipient(self):
        return self._recipient

    message_id: int = None  # Sequence number of this message. Makes it unique for this node.
    data: str = None
    _recipient: str = address_broadcast     # Broadcast address
    pid: int = 0
    _sender: str = None
    sender_pid: int = 0
    time: time = None
    sequence_number: int = 0  # Number of this package for the message
    _message_sender_header: int = 0
    _related_packages: int = 0  # How many other packages for this message
    _header_to: int = None
    _header_id: int = 0

    def __str__(self) -> str:
        """
        For printing only
        :return:
        """
        return "Message{\nto:" + str(self.recipient) + ",\nfrom:" + self._sender + ",\ndata:" + self.data \
               + ",\nsequence_number:" + str(self.sequence_number) + ",\nrelated_packages:" \
               + str(self._related_packages) + "\nmessage_id:" + str(self.message_id) \
               + "\nmessage_sender_header:" + str(self._message_sender_header) + "\n}"

    def combine(self, message: Message) -> bool:
        """
        Combines two messages into self. Combination only happens if the data of the messages is consecutive.
        :param message: to be combined
        :return: True in case the messages were combined, false otherwise.
        """
        # Two packages for the same message checks
        logging.debug("Combining messages")
        valid: bool = True
        if message.message_id != self.message_id: valid = False
        if message.recipient != self.recipient: valid = False
        if message.pid != self.pid: valid = False
        if message._sender != self._sender: valid = False
        if message.sender_pid != self.sender_pid: valid = False
        if message.sequence_number > self._related_packages: valid = False
        if message.related_packages < self.sequence_number: valid = False
        if message._message_sender_header != self._message_sender_header: valid = False
        if not valid:
            logging.info(message)
            logging.info(self)
            logging.info("\n\n\n")

        self.data += message.data
        return True

    @property
    def sender(self) -> str:
        return self._sender

    @sender.setter
    def sender(self, sender: str):
        self._sender = sender
        self._message_sender_header = int.from_bytes(bytes.fromhex(self._sender[-2:]), byteorder='big', signed=False)

    @property
    def related_packages(self):
        return self._related_packages

    @related_packages.setter
    def related_packages(self, value: int):
        self._related_packages = value

    @property
    def message_sender_header(self):
        return self._message_sender_header

    @recipient.setter
    def recipient(self, recipient):
        self._recipient = recipient
        self._header_to = int.from_bytes(bytes.fromhex(recipient[-2:]), byteorder='big', signed=False)

    def split(self) -> [packageType]:
        """
        Split message to packages. data will be prependet with the headers.
        """
        logging.debug("Retrieving next package")
        # Everything sent already
        if self.data is None or self.data == "":
            return None

        try:
            # Headers
            header_from = self._message_sender_header
            header_to = self._header_to
            header_id = self._header_id

            # To
            b = bytes.fromhex(self.recipient) + self.pid.to_bytes(length_pid, byteorder='big')
            # From
            b += bytes.fromhex(self._sender) + self.sender_pid.to_bytes(length_pid, byteorder='big')

            # Message id
            b += self.message_id.to_bytes(length_message_id, byteorder='big')

            # data
            data_bytes: bytes = self.data.encode()

            # how many packages are sent header
            num_packages: int = math.ceil(len(data_bytes) / length_max_data)
            # max id.
            num_packages -= 1
            # to bytes
            num_packages_bytes = num_packages.to_bytes(math.floor(length_sequence_number / 2), byteorder='big')
            b += num_packages_bytes

            # Check for invalid metadata
            if len(b) > length_meta - (length_sequence_number / 2):
                raise Exception("Invalid meta data")

            seq_num = 0
            # split message
            result: [packageType] = []
            while len(data_bytes) > 0:
                seq_str: bytes = seq_num.to_bytes(math.floor(length_sequence_number / 2), byteorder='big')
                seq_num += 1

                meta: bytes = b + seq_str

                data: bytes = data_bytes[:length_max_data]

                # Add error detection
                payload: bytes = meta + data
                payload = add_check(payload)

                data_bytes = data_bytes[len(data):]

                # Headers
                result.append((header_to, header_from, header_id, 0, payload))
            return result
        except Exception as e:
            logging.error("Error while splitting message: " + str(e))
            return []
