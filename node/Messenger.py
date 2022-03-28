import logging
import threading
from node.RFMWrapper import RFMWrapper
from node.MessageStorage import MessageStorage
from node.Message import Message
from node.MessageOrganiser import MessageOrganiser
from node.Exceptions import MalformedContentException
from util.Utilities import *


class Messenger:

    _active: bool = True

    _rfm95: RFMWrapper = None  # Access transponder
    _organiser: MessageOrganiser = None
    node_id: str = None

    def __init__(self):
        self._rfm95 = RFMWrapper()
        self.node_id = read_uuid_file(read_config_file("uuid_file"))
        self._organiser = MessageOrganiser(self.node_id)
        super().__init__()

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages
        :return: void
        """
        logging.info("Started node with id: " + self.node_id)
        t = threading.Thread(target=self._organiser.run)
        t.start()
        logging.info("Hearst")
        while self._active:
            try:
                logging.debug("Checking for messages")
                received: Message = self._rfm95.receive()  # Receive new message
                if received:                              # Check if something was received
                    self._organiser.push_to_received(received)  # Add to relevant queues and lists
                    continue  # attempt receiving more messages before sending  PRIORITY ON FORWARDING / RECEIVING

                # Check send queue
                package: Message = self._organiser.pop_from_send()

                # Nothing to send
                if package is None:
                    continue

                # package to be sent
                if self._rfm95.send(package):
                    logging.info("Sent package")
                else:
                    logging.error("Could not send package")
                    self._organiser.push_to_send(package)
            except KeyboardInterrupt as e:
                self._active = False
                logging.error("Shutting down" + str(e))
            except MalformedContentException as e:
                logging.error("Error while sending message: " + str(e))
            except Exception as e:
                # No user option to handle error so try to keep up operations.
                logging.error("Unhandled exception. Continuing operation" + str(e))

        self._organiser.stop()
        t.join()

        logging.info("Shut down Messenger")

    def send(self, data: Message):
        """
        Add message to send queue, if it not destined for this node.
        The sender of the message will be set to this node.
        :param data: message to be sent.
        :return: void.
        """
        if data.recipient == self.node_id:
            return
        logging.info("Adding message to send queue")
        data.sender = self.node_id
        self._organiser.push_to_send(data)
