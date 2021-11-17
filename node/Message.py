class Message:

    data = None
    recipient = None
    pid = None


def from_bytes(bytes):
    if not bytes:
        return None
    print(bytes)
    m = Message()
    m.recipient = bytes[:16]
    m.pid = bytes[16:21]
    m.data = bytes[21:]
    return m

