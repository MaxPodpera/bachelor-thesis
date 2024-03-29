import logging
import threading
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
from src.RFMWrapper import RFMWrapper
from src.Message import Message
from src.MessageOrganiser import MessageOrganiser
from src.Exceptions import MalformedContentException
from src.Utilities import *


class Messenger:
    """
    Class to handle messages on the top level.

    """
    _active: bool = True  # keep running

    _rfm95: RFMWrapper = None  # Access transponder
    _organiser: MessageOrganiser = None
    node_id: str = None  # Network id of this network

    def __init__(self):
        """
        Load id and create objects for task delegation.
        """
        self._rfm95 = RFMWrapper()
        self.node_id = read_uuid_file(read_config_file("uuid_file"))
        self._organiser = MessageOrganiser(self.node_id)
        super().__init__()

    def run(self):
        """
        Check transmitter for incoming messages and send outgoing messages.
        Runs until stop() is called.
        :return: void
        """
        logging.info("Started node with id: " + self.node_id)
        t = threading.Thread(target=self._organiser.run)
        t.start()
        while self._active:
            try:
                received: Message = self._rfm95.receive()  # Receive new message
                if received:                              # Check if something was received
                    if self.node_id == "17109be4e4b711ec8fea0242ac120002": # ignore not forwarded packages
                        if "A" in received.data:
                            continue
                    if self.node_id == "2b679c67277302db4ca0ae3fcbad51d3":
                        received.data = received.data.replace("A", "B")

                    self._organiser.push_to_received(received)  # Add to relevant queues and lists
                    continue  # attempt receiving more messages before sending  PRIORITY ON FORWARDING / RECEIVING

                # Check send queue
                package: Message = self._organiser.pop_from_send()

                # Nothing to send
                if package is None:
                    continue

                # package to be sent
                residue: Message = self._rfm95.send(package)
                if residue is None:
                    logging.info("Sent package")
                else:
                    logging.error("Could not send (entire) package")
                    self._organiser.push_to_send(residue)
            except KeyboardInterrupt as e:
                self._active = False
                logging.error("Shutting down" + str(e))
            except MalformedContentException as e:
                logging.error("Error while sending message: " + str(e))
            except Exception as e:
                # No user option to handle error so try to keep up operations.
                logging.error("Unhandled exception. Continuing operation: " + str(e))
        self._organiser.stop()  # Stop the organiser
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

    def stop(self):
        """
        Stop the messenger.
        """
        self._active = False
