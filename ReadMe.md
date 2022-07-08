# Mesh-Lora

This repository was developed for my bachelor-thesis at the technical University of Vienna as part of a project for the 
firebrigard in lower austria.

Based on the adafruit_rfm9x library it allows to send messages over the adafruit rfm9x module.
compared to the native library however, a greater address range as well as larger messages are possible (sent as multiple packages).

## How to run

### Module connection
The first step is to connect the raspberry pi to the module, as shown below.

| Pi        | rfm9x| 
|-----------|------|
| 3.3V      | VIN  |
| GND       | GND  |
| GPIO 5    | G0   |
| GPIO 25   | RST  |
| SCK       | CLK  |
| MISO      | MISO |
| MOSI      | MOSI |
| CE1       | CS   |

### Setting options
Per default the repository should contain a `config.yaml` file.
Here the options for the program can be set.

The options specified there are (The default can be seen below):

* uuid_file: path to a file containing the id of the node. e.g. `2b679c67277302db4ca0ae3fcbad51d3`
* message_folder: path to a folder for storing and reading messages. Received messages will be stored here. File created
according to the naming convention will be read and sent.
* message:
    * ms_memorize_received_message_id: time to memorize that a message was received already-
    * broadcast_address: address that will be recognized as broadcast address.
    * meta:
        * length_id: length of the node id in bytes.
        * length_pid: length of the pid for addressing messages in bytes.
        * length_frame: total length of message in bytes.
        * length_message_id: length of the message id in bytes.
        * length_sequence_number: length of the sequence number for messages in bytes.
```
uuid_file: 
message_folder: "./storage/" # "~/tmp/lora"
message:
  ms_memorize_received_message_id: 50000
  broadcast_address: "00000000000000000000000000000000"
  meta:
    length_id: "16"
    length_pid: "2"
    length_frame: "124"  # "100" # 252
    length_message_id: "1"
    length_sequence_number: "4"  # expected to be even length
```
### Running
To run the project it first has to be downloaded from github using git clone.

After installing the requirements (`pip3 install requirements.txt`), the program can then be run using
`python3 ./src/main.py ./src/config.yaml`

To send messages a file has to be created in the folder specified by the `message_folder` option.
The name of the file should be of the form: `OUT_[SENDER-PID]_[RECIPIENT]_[RECIPIENT-PID]`.
 * `OUT`: Marks files that should be transmitted
 * ``[SENDER-PID]``: The process id of the process sending the message.
 * ``[RECIPIENT]``: The address of the recipient.
 * ``[RECIPIENT-PID]``: The pid of the process that should be addressed.

The file content then corresponds with the messages content.

Upon receiving a message, a file is created following the pattern ```IN_[PID]_[SENDER]_[SENDER-PID]_[Message-id]```.
* `IN`: marks the message as received. A process utilizing this project can scan the folder for messages starting with `IN` to check for incoming messages.
* ``[PID]``: The process id of the recipient process.
* ``[SENDER]``: The adress of the sender. Can be used to send responses.
* ``[SENDER-PID``: The pid of the sender. Also to be used for responses
* ``[Message-id]``: To guarantee uniqueness of filenames.

