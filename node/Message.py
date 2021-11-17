class Message:

    data = None
    recipient = None
    pid = None

    def __str__(self):
        return "Message{to:" + self.pid + ",at:" + self.recipient + ",data:"+ self.data + "}"

def from_bytes(bytes):
    if not bytes:
        return None
    print(bytes)
    m = Message()
    m.recipient = bytes[:16].decode("utf-8")
    m.pid = bytes[16:21].decode("utf-8")
    m.data = bytes[21:].decode("utf-8")
    return m

