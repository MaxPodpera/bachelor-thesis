import time


class Message:

    data: str = None
    recipient: str = None
    pid: int = None
    sender: str = "0000000000000000"
    sender_pid: int = 00000
    time: time = None

    def __str__(self):
        """
        For printing only
        :return:
        """
        return "Message{to:" + str(self.pid) + ",at:" + self.recipient + ",data:" + self.data + "}"


# TODO: real value and setter oder so
max_data_length = 251


def from_bytes(bytes_to_convert: bytearray) -> Message:
    if not bytes_to_convert:
        return None
    m = Message()
    m.recipient = bytes_to_convert[:16].decode("utf-8")
    m.pid = bytes_to_convert[16:21].decode("utf-8")
    m.sender = bytes_to_convert[21:37].decode("utf-8")
    m.sender_pid = bytes_to_convert[37:42].decode("utf-8")
    m.data = bytes_to_convert[42:].decode("utf-8")
    m.time = time.time()
    return m


def to_bytes(message: Message) -> [bytearray]:
    result = []
    if not message:
        return result

    # conversion
    b  = bytearray(message.recipient.encode()) + bytearray(str(message.pid).encode())
    b += bytearray(message.sender.encode()) + bytearray(str(message.sender_pid).encode())
    data_bytes = bytearray(message.data.encode())

    # split message
    while len(data_bytes) > 0:
        result.append(b + data_bytes[:(max_data_length - len(b))])
        data_bytes = data_bytes[max_data_length:]

    return result
