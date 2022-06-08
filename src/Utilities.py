import yaml
import sys
import logging
from src.Exceptions import InvalidConfigurationException


def read_uuid_file(path) -> str:
    """
    Read UUID from a file. Is expected to be the first line of the file. No checks are performed. On failure an empty string is returned
    else the UUID as string is returned
    :param path: to the file
    :return: "" on Failure the UUID otherwise
    """
    try:
        with open(path) as fp:
            line = fp.readline()
            if not line:
                return ""
            return line[:-1]    # remove newline
    except Exception as e:
        return ""


def read_config_file(key: str) -> str:
    """
    Read value form config file. Expected to be a yaml file.
    :param key:
    :return:
    """
    try:
        with open(sys.argv[1], 'r') as file:
            config = yaml.safe_load(file)
            value = config
            for k in key.split("."):
                value = value[k]
            if value is None:
                return ""
        return value
    except Exception as e:
        logging.error("Could not read config file: " + str(e))
        raise InvalidConfigurationException(e)


def write_or_append_to_file(data: str) -> None:
    try:
        with open("statistics_case2_1sec_1pck_10sec_5sec_1sec_3pck_100msg.csv", 'a') as file:
            file.write(data)
        return None
    except Exception as e:
        logging.error("Couldn't append")
        raise InvalidConfigurationException(e)