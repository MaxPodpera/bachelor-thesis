import getopt
import os
import time
import sys
import json
import inotify.adapters

NAME = "mesh"
SYNC_FOLDER_PATH = ""  # "./tmp/" + NAME + "/"


def unpack():
    """
    Unpack the cli options. Does not check for any exceptions.
    :return: [(type,type)], [type] where the first array contains tuples. The first element
    is the name of the option the second one is the argument given to it. The second array
    contains the positional argument.
    """
    return getopt.getopt(
        sys.argv[1:],
        "hf:d:",
        ["destination=", "file=", "help"]
    )


def usage():
    """
    Returns the usage for the cli
    :return: string with explaination for the options for this cli
    """
    return sys.argv[0] + " [destination] message"


def parse(args):
    """
    Parse arguments into a json to transfer to the lora interface
    :param args: parse cl arguments
    :return: json to be passed to the lora interface containing information about what should be done.
    """
    info = {
        "destination": 255,
        "data": ""
    }
    if len(args) >= 2:
        info["destination"] = args[1]
    for i in range(2, len(args)):
        info["data"] += args[i] + " "
    info["data"] = info["data"][:-1]
    return info


def send_to_transciever(data):
    # if not os.path.exists(SYNC_FOLDER_PATH):
    #    print("\033[91mInvalid configuration could not find " + SYNC_FOLDER_PATH + '\033[0m')
    #    return False
    file_name = "out_" + str(os.getpid()) + "_" + str(time.time()) + ".json"
    print(file_name)
    print(data)
    with open(SYNC_FOLDER_PATH + file_name, "w") as out_file:
        json.dump(data, out_file)
    return file_name


if __name__ == '__main__':
    try:
        information = parse(sys.argv)  # create json for sending process
        if information["data"] != "":  # in case of -h option information is None
            file = send_to_transciever(information)

        i = inotify.adapters.Inotify()
        i.add_watch(SYNC_FOLDER_PATH)

        for event in i.event_gen(yield_nones=False):
            _, type_names, path, filename = event
            print(event)

    except getopt.GetoptError as e:
        print("\033[91mError: " + str(e) + '\033[0m')
        print(usage())
