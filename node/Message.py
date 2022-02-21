from __future__ import annotations
import time
import math
from util.Utilities import read_config_file

"""
Message class. Contains definition of the Messages and functionality to convert messages to bytes and the other way around.
"""
print(read_config_file("uuid_file"))
print(read_config_file("message.meta"))
print(read_config_file("message.meta.length_id"))
print(int(read_config_file("message.meta.length_id")))
print("oida he")
length_node_id: int = int(read_config_file("message.meta.length_id"))
length_pid: int = int(read_config_file("message.meta.length_pid"))
length_frame: int = int(read_config_file("message.meta.length_frame"))
length_message_id: int = int(read_config_file("message.meta.length_message_id"))
length_sequence_number: int = int(read_config_file("message.meta.length_sequence_number"))  # length is expected to be of
# even length
length_meta: int = (length_node_id * 2) + (length_pid * 2) + length_sequence_number + length_message_id
length_max_data: int = length_frame - length_meta

address_broadcast: str = read_config_file("message.broadcast_address")


class Message:

    message_id: int = 0
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


def from_bytes(bytes_to_convert: bytearray) -> Message:
    """
    Convert a bytearray to a Message object. If the bytearray is invalid (length or None) None is returned.
    :param bytes_to_convert: bytearray to be converted. The array is expected to be of the form:
    |sender|sender_pid|recipient|recipient_pid|id|related_packages|seq_num|data
    :return: Message object on success None on failure
    """
    if not bytes_to_convert:
        return None
    if len(bytes_to_convert) <= length_meta:
        return None

    next_part_index: int = length_node_id
    m: Message = Message()

    # From
    m.recipient = bytes_to_convert[:next_part_index].decode("utf-8")
    m.pid = int(bytes_to_convert[next_part_index: next_part_index + length_pid].decode("utf-8"))
    next_part_index += length_pid

    # To
    m.sender = bytes_to_convert[next_part_index: next_part_index + length_node_id].decode("utf-8")
    next_part_index += length_node_id
    m.sender_pid = int(bytes_to_convert[next_part_index: next_part_index + length_pid].decode("utf-8"))
    next_part_index += length_pid

    # id
    m.message_id = int(bytes_to_convert[next_part_index: next_part_index + length_message_id])
    next_part_index += length_message_id

    # Sequence Number
    m._related_packages = int(bytes_to_convert[next_part_index: next_part_index + math.floor(length_sequence_number / 2)])
    next_part_index += math.floor(length_sequence_number / 2)
    m.sequence_number = int(bytes_to_convert[next_part_index: next_part_index + math.floor(length_sequence_number / 2)])
    next_part_index += math.floor(length_sequence_number / 2)

    # Data
    m.data = bytes_to_convert[next_part_index:].decode("utf-8")

    # Time
    m.time = time.time()
    return m


def to_bytes(message: Message) -> [bytearray]:
    """
    Convert message to bytes according to message specification. If Data is to long for transmission in one package
    multiple will be generated. If they exceed the max number of packages within a sequence, packages with the next
    message id will be generated.
    :param message: to be converted
    :return: array containing each message that has to be sent.
    """
    result = []
    if not message:
        return result

    # conversion

    # To
    b: bytearray = bytearray(message.recipient.encode()) + bytearray(str(message.pid).encode())
    # From
    b += bytearray(message.sender.encode()) + bytearray(str(message.sender_pid).encode())
    # id
    b += bytearray(('0' * (length_message_id - len(str(message.message_id).encode())) + str(message.message_id)).encode())

    # data.
    data_bytes: bytearray = bytearray(message.data.encode())

    # how many packages are sent header
    num_packages: int = math.ceil(len(data_bytes) / length_max_data)

    # To many packages to send as one message. Give next message id.
    if len(str(num_packages)) > (length_sequence_number / 2):
        message.message_id += 1                       # Next message
        # num_packages for this id
        num_packages = int(math.pow(10, length_sequence_number / 2))
        # bytes sent with first id
        bytes_with_first_id: int = num_packages * length_max_data
        # adjust data
        message.data = message.data[bytes_with_first_id:]
        # packages with next id
        result = to_bytes(message)

    # max id.
    num_packages -= 1

    str_num_packages: str = '0' * (math.floor(length_sequence_number / 2) - len(str(num_packages))) + str(num_packages)

    if len(str_num_packages) > math.floor(length_sequence_number / 2):
        raise Exception("Invalid amount of packages: " + str(str_num_packages) + " > " + str(math.floor(length_sequence_number / 2)))

    b += bytearray(str_num_packages.encode())

    # Check for invalid metadata
    if len(b) > length_meta - (length_sequence_number / 2):
        raise Exception("Invalid meta data")

    seq_num = 0

    # split message
    while len(data_bytes) > 0:
        seq_str = '0' * (math.floor(length_sequence_number / 2) - len(str(seq_num))) + str(seq_num)  # always same length

        if len(seq_str) > math.floor(length_sequence_number):  # return everything that could receive a sequence number
            raise Exception("Attempting to use too high sequence number")

        meta = b + seq_str.encode()
        data = data_bytes[:length_max_data]
        result.append(meta + data)
        data_bytes = data_bytes[len(data):]
        seq_num += 1

    return result
