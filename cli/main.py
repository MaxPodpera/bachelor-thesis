import getopt
import os
import time
import sys
import json
NAME = "mesh"
SYNC_FOLDER_PATH = ""#"./tmp/" + NAME + "/"


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
    return NAME + "[-h] [-d Integer] [-f Path]\n" \
        "   [-h]       prints this information.\n" \
        "   [-d]       destination for the package to be sent. 255 is used as default.\n" \
        "   [-f Path]  file containing the data to be sent. Otherwise data is expected as first argument.\n "


def parse(parsed_args):
    """
    Parse arguments into a json to transfer to the lora interface
    :param parsed_args: parse cl arguments
    :return: json to be passed to the lora interface containing information about what should be done.
    """
    info = {
        "destination": None,
        "data": None,
        "output_to": None,
    }
    options, arguments = parsed_args
    if ('-h', '') in options:  # Print usage
        print(usage())
        return None
    for opt in options:
        if '-d' in opt:
            _, info["destination"] = opt
        if '-f' in opt:
            _, info["output_to"] = opt

    # Get data to be sent
    if len(arguments) < 1:
        raise getopt.GetoptError("Data required")
    info["data"] = arguments[0]
    return info


def validation(information):
    return None


def send_to_transciever(data):
    #if not os.path.exists(SYNC_FOLDER_PATH):
    #    print("\033[91mInvalid configuration could not find " + SYNC_FOLDER_PATH + '\033[0m')
    #    return False
    file_name = "out_" + str(os.getpid()) + "_" + str(time.time()) + ".json"
    print(file_name)
    print(data)
    with open(SYNC_FOLDER_PATH + file_name, "w") as out_file:
        json.dump(data, out_file)


if __name__ == '__main__':
    try:
        parsed_args = unpack()  # Get cl arguments
        information = parse(parsed_args)  # create json for sending process
        if information is not None:  # in case of -h option information is None
            validation(information)  # validate options
            send_to_transciever(information)
    except getopt.GetoptError as e:
        print("\033[91mError: " + str(e) + '\033[0m')
        print(usage())
