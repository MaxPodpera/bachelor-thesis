import math

length_node_id: int = int(read_config_file("message.meta.length_id"))
length_pid: int = int(read_config_file("message.meta.length_pid"))
length_frame: int = int(read_config_file("message.meta.length_frame"))
length_message_id: int = int(read_config_file("message.meta.length_message_id"))
length_sequence_number: int = int(read_config_file("message.meta.length_sequence_number"))  # length is expected to be of
# even length
length_meta: int = (length_node_id * 2) + (length_pid * 2) + length_sequence_number + length_message_id
length_max_data: int = length_frame - length_meta

address_broadcast: str = read_config_file("message.broadcast_address")


class Packet:
    #         to  from  id   flags
    headers: (int, int, int, int) = (255, 255, 0, 0)
    b: bytearray

    def __init__(self, headers: (int, int, int, int), data_bytes: bytearray):
        self.headers = headers
        self.b = data_bytes

    def to_message(self) -> Message:
        if not self.b or not self.headers:
            return None

        next_part_index: int = Packet.length_node_id
        m: Message = Message()

        _, _, m.message_id, _ = self.headers

        # To
        m.recipient = bytes_to_convert[:next_part_index].hex()
        m.pid = int.from_bytes(bytes_to_convert[next_part_index: next_part_index + Packet.length_pid], byteorder='big',
                               signed=False)
        next_part_index += length_pid

        # From
        m.sender = bytes_to_convert[next_part_index: next_part_index + Packet.length_node_id].hex()
        next_part_index += length_node_id
        m.sender_pid = int.from_bytes(bytes_to_convert[next_part_index: next_part_index + Packet.length_pid],
                                      byteorder='big', signed=False)
        next_part_index += length_pid

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
        return m


def from_data(data: bytes) -> Packet:
    return Packet(data[:4], data[4:])
    

def from_message(message: Message) -> [Packet]:
    # Headers
    to_id, from_id, m_id, flags = 255, 255, message.message_id, 0
    headers = to_id, from_id, m_id, flags

    # To
    b = bytes.fromhex(message.recipient) + message.pid.to_bytes(length_pid, byteorder='big')
    # From
    b += bytes.fromhex(message.sender) + message.sender_pid.to_bytes(length_pid, byteorder='big')
    # id
    b += message.message_id.to_bytes(length_message_id, byteorder='big')

    # data
    data_bytes: bytearray = bytearray(message.data.encode())

    # how many packages are sent header
    num_packages: int = math.ceil(len(data_bytes) / length_max_data)
    # max id.
    num_packages -= 1
    # to bytes
    num_packages_bytes = num_packages.to_bytes(math.floor(length_sequence_number / 2), byteorder='big')
    self.b += num_packages_bytes

    # Check for invalid metadata
    if len(self.b) > length_meta - (length_sequence_number / 2):
        raise Exception("Invalid meta data")

    seq_num = 0
    result = [Packet]
    # split message
    while len(data_bytes) > 0:
        seq_str = seq_num.to_bytes(math.floor(length_sequence_number / 2), byteorder='big')
        seq_num += 1

        meta = b + seq_str
        data = data_bytes[:length_max_data]
        result.append(Packet(headers, meta + data))
        
        data_bytes = data_bytes[len(data):]

    return result
