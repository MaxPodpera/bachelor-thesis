class Message:

    data = None
    recipient = None
    pid = None

    def __str__(self):
        return "Message{to:" + self.pid + ",at:" + self.recipient + ",data:"+ self.data + "}"


# TODO: real value and setter oder so
max_data_length = 251


def from_bytes(bytes: bytearray) -> Message:
    if not bytes:
        return None
    print(bytes)
    m = Message()
    m.recipient = bytes[:16].decode("utf-8")
    m.pid = bytes[16:21].decode("utf-8")
    m.data = bytes[21:].decode("utf-8")
    return m


def to_bytes(message: Message) -> [bytearray]:
    if not message:
        return []

    result = []
    b = bytearray(message.recipient.encode()) + bytearray(str(message.pid).encode())
    data_bytes = bytearray(message.data.encode())
    print(data_bytes)
    print(len(data_bytes))
    while len(data_bytes) > 0:
        result.append(b + bytearray(data_bytes[(max_data_length - len(b)):]))
        print(b + bytearray(data_bytes[(max_data_length - len(b)):]))  #
        data_bytes = data_bytes[max_data_length:]

    return result
