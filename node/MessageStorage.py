class MessageStorage:

    folder = "/tmp/lora"  # folder to store messages

    def __init__(self):
        pass

    def store(self, message, incoming=True):
        """
        Store a given message returns the identifier to retrieve the message again
        :param message: to be stored
        :return: identifier to retrieve it again
        """
        if incoming:
            return "IN_" + message.pid + "_" + ""
        return ""

    def get(self, identifier):
        pass