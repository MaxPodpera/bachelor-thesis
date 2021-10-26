import sys
import time
import json

if __name__ == '__main__':

    file_name = "out_" + str(sys.argv[1]) + "_" + str(time.time()) + ".json"
    print(file_name)
    data = {'data': 'some dummy data'}
    with open("./" + file_name, "w") as out_file:
        json.dump(data, out_file)
