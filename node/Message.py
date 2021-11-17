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
    m.recipient = str(bytes[:16])
    m.pid = str(bytes[16:21])
    m.data = str(bytes[21:])
    return m

