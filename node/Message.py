import time

"""
Message class. Contains definition of the Messages and functionality to convert messages to bytes and the other way around.
"""

length_node_id: int = 32
length_pid: int = 5
length_time: int = 13
length_frame: int = 255
length_sequence_number: int = 8
length_meta: int = (length_node_id * 2) + (length_pid * 2) + length_time + length_sequence_number
length_max_data: int = length_frame - length_meta

address_broadcast: str = "00000000000000000000000000000000"


class Message:

    data: str = None
    recipient: str = address_broadcast     # Broadcast address
    pid: int = -1
    sender: str = "00000000000000000000000000000000"
    sender_pid: int = -1
    time: time = None
    sequence_number: int = -1

    def __str__(self) -> str:
        """
        For printing only
        :return:
        """
        return "Message{to:" + str(self.pid) + ",at:" + self.recipient + ",data:" + self.data + "}"


def from_bytes(bytes_to_convert: bytearray) -> Message:
    """
    Convert a bytearray to a Message object. If the bytearray is invalid (length or None) None is returned.
    :param bytes_to_convert: bytearray to be converted
    :return: Message object on success None on failure
    """
    if not bytes_to_convert:
        return None
    if len(bytes_to_convert) <= length_meta:
        return None

    # TODO handle pids like 00001 str(00001) = 1
    next_part_index = length_node_id
    m = Message()
    # From
    m.recipient = bytes_to_convert[:next_part_index].decode("utf-8")
    m.pid = bytes_to_convert[next_part_index: next_part_index + length_pid].decode("utf-8")

    next_part_index += length_pid

    # To
    m.sender = bytes_to_convert[next_part_index: next_part_index + length_node_id].decode("utf-8")
    next_part_index += length_node_id
    m.sender_pid = bytes_to_convert[next_part_index: length_pid].decode("utf-8")
    next_part_index += length_pid

    # Sequence Number
    m.sequence_number = int(bytes_to_convert[next_part_index: next_part_index + length_sequence_number])
    next_part_index += length_sequence_number

    # Data
    m.data = bytes_to_convert[next_part_index:].decode("utf-8")

    # Time
    m.time = time.time()
    return m


def to_bytes(message: Message) -> [bytearray]:
    """
    Convert message to bytes according to message specification. If Data is to long for transmission multiple messages will be generated.
    :param message: to be converted
    :return: array containing each message that has to be sent.
    """
    result = []
    if not message:
        return result

    # conversion
    b = bytearray(message.recipient.encode()) + bytearray(str(message.pid).encode())
    b += bytearray(message.sender.encode()) + bytearray(str(message.sender_pid).encode())

    if len(b) > length_meta - length_sequence_number:
        raise Exception("Invalid meta data")

    data_bytes = bytearray(message.data.encode())

    seq_num = 0

    # split message
    while len(data_bytes) > 0:
        seq_str = '0' * (length_sequence_number - len(str(seq_num)) - 1) + str(seq_num)  # always same length
        if len(seq_str) > length_sequence_number:  # return everything that could receive a sequence number
            return result

        seq_num += 1

        result.append(b + seq_str.encode() + data_bytes[:(length_max_data - len(b))])
        data_bytes = data_bytes[(length_max_data - len(b)):]

    return result
