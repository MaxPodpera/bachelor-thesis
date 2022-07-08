import logging
import os
import inotify.adapters
from src.Utilities import read_config_file
from src.Message import Message
from typing import Union


class MessageStorage:
    """
    Message storage class.
    """

    _active: bool = True
    _folder = read_config_file("message_folder")  # folder to store messages
    _new_message: [Message] = []
    _to_storage: [Message] = []

    def __init__(self):
        # Create the folder for the files
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)
            logging.info("Created sync folder")
            return
        logging.debug("Sync folder exists")

    def store(self, message):
        """
        Store message in storage
        """
        logging.info("Send message to storage")
        self._store(message)

    def _store(self, message: Message):
        """
        Store a given message returns the identifier to retrieve the message again
        :param message: to be stored
        :return: identifier to retrieve it again
        """
        try:
            logging.debug("Storing message")
            # Generate filename
            # IN_[PID]_[SENDER]_[SENDER-PID]_[Message-id]
            file_name = "_".join(["IN", str(message.pid), message.sender, str(message.sender_pid), str(message.message_id)])
            path = os.path.join(self._folder, file_name)
            # Create the file
            with open(path, 'w') as f:
                f.write(message.data)
            logging.info("Message stored")
        except FileExistsError:
            logging.error("Could not create file for storage")

    def _get(self, identifier) -> Union[Message, None]:
        """
        Load a file from the folder to send message.
        :param identifier: for the file to be loaded
        :return: Message object representing the file.
        """
        try:
            message: Message = Message()
            infos = [info for info in identifier.split("_")]

            # OUT_SENDER-PID_RECIPIENT_RECIPIENT-PID
            message.pid = int(infos[3])
            message.recipient = infos[2]
            message.sender_pid = int(infos[1])

            with open(os.path.join(self._folder, identifier), "r") as file:
                message.data = file.read()

            logging.info("Loaded message")
            return message
        except Exception as e:
            logging.error("Could not load message: " + str(e))
            return None

    def _delete(self, identifier) -> bool:
        """
        Delete message file
        :param identifier:
        :return:
        """
        path = os.path.join(self._folder, identifier)
        if os.path.exists(path):
            os.remove(path)
            return True
        else:
            logging.debug("The file does not exist")
            return False

    def get(self) -> Union[Message, None]:
        """
        If new files were added to the specified folder, they are converted to messages and returned. If none were created
        None is returned
        :return: None or a new Message.
        """
        try:
            return self._new_message.pop(0)
        except IndexError as e:
            return None

    def run(self):
        """
        Watch folder for new files. If new files appear parse them to messages and add to list so they can be retrieved
        by the get method.
        :return:
        """

        i_notify = inotify.adapters.Inotify()
        i_notify.add_watch(self._folder)

        for event in i_notify.event_gen(yield_nones=False):
            if not self._active:
                break
            _, type_names, _, filename = event

            if 'IN_CLOSE_WRITE' in type_names:
                logging.info("Detected write event")
                if "OUT" in filename:
                    logging.debug("OUT file found")
                    self._new_message.append(self._get(filename))
                    self._delete(filename)

        logging.info("Stopped storage")

    def stop(self):
        """
        Stop the storage. No more file system events will be detected.
        """
        self._active = False
